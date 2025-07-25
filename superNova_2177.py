from typing import Dict, Any, List
from collections import defaultdict
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ImmutableTriSpeciesAgent(RemixAgent):
    """
    Subclass enforcing Tri-Species governance: immutable 1/3 weight per species,
    >50% averaged yes for normal, >90% for constitutional changes (dynamic via Lorenz curve/Gini),
    ≥10% internal yes per species. Logs violations if prior logic changed without vote.
    """
    SPECIES = ['human', 'ai', 'company']  # Immutable; changes need supermajority vote
    NORMAL_THRESHOLD = Decimal('0.5')
    BASE_CONSTITUTIONAL_THRESHOLD = Decimal('0.9')
    MAX_CONSTITUTIONAL_THRESHOLD = Decimal('0.95')
    INTERNAL_SPECIES_THRESHOLD = Decimal('0.1')
    MIN_VOTERS_PER_SPECIES = 1  # Minimum votes per species for valid tally

    def _calculate_gini_coefficient(self, species_totals: Dict[str, Decimal]) -> Decimal:
        """
        Calculate Gini coefficient from vote distribution across species.
        - Sort species by vote count, compute Lorenz curve, and derive Gini (0 = equal, 1 = max inequality).
        - Used to adjust constitutional threshold dynamically.
        """
        vote_counts = [species_totals[s] for s in self.SPECIES]
        if not vote_counts or sum(vote_counts) == 0:
            return Decimal('0')  # No votes, assume equal distribution

        sorted_votes = sorted(vote_counts)
        n = len(sorted_votes)
        cumulative_votes = sum(sorted_votes)
        if cumulative_votes == 0:
            return Decimal('0')

        # Lorenz curve: cumulative share of votes
        cumulative_share = 0
        area_under_lorenz = Decimal('0')
        for i, vote in enumerate(sorted_votes, 1):
            cumulative_share += vote
            area_under_lorenz += cumulative_share / cumulative_votes

        # Gini = 1 - 2 * (area under Lorenz curve) / n
        gini = Decimal('1') - Decimal('2') * area_under_lorenz / Decimal(n)
        return max(Decimal('0'), min(gini, Decimal('1')))  # Clamp to [0, 1]

    def _get_dynamic_threshold(self, species_totals: Dict[str, Decimal], is_constitutional: bool) -> Decimal:
        """
        Dynamically adjust threshold based on vote inequality (Gini coefficient).
        - Normal proposals: 0.5
        - Constitutional: 0.9 (Gini=0) to 0.95 (Gini≥0.5)
        """
        if not is_constitutional:
            return self.NORMAL_THRESHOLD

        gini = self._calculate_gini_coefficient(species_totals)
        # Linearly scale threshold: 0.9 (Gini=0) to 0.95 (Gini≥0.5)
        threshold = self.BASE_CONSTITUTIONAL_THRESHOLD
        if gini > Decimal('0.5'):
            threshold = self.MAX_CONSTITUTIONAL_THRESHOLD
        elif gini > Decimal('0'):
            threshold += (self.MAX_CONSTITUTIONAL_THRESHOLD - self.BASE_CONSTITUTIONAL_THRESHOLD) * gini / Decimal('0.5')

        total_voters = sum(species_totals.values())
        logger.info(f"Dynamic threshold for {total_voters} voters, Gini {gini:.4f}: {threshold:.4f}")
        return threshold

    def _apply_VOTE_PROPOSAL(self, event: Dict[str, Any]):
        proposal_id = event['proposal_id']
        voter = event['voter']
        vote = event['vote'].lower()

        proposal = self.storage.get_proposal(proposal_id)
        if not proposal:
            raise InvalidEventError(f"Proposal {proposal_id} not found")

        voter_data = self.storage.get_user(voter)
        if not voter_data:
            raise InvalidEventError(f"Voter {voter} not found")

        species = voter_data['species'].lower()
        if species not in self.SPECIES:
            raise InvalidEventError(f"Invalid species: {species}")

        # Record vote
        if 'votes' not in proposal:
            proposal['votes'] = defaultdict(dict)
        proposal['votes'][species][voter] = vote

        # Tally votes per species
        species_yes = {s: Decimal('0') for s in self.SPECIES}
        species_total = {s: Decimal('0') for s in self.SPECIES}

        for s in self.SPECIES:
            votes_in_species = proposal['votes'].get(s, {})
            total_in_species = len(votes_in_species)
            species_total[s] = Decimal(total_in_species)
            if total_in_species > 0:
                yes_in_species = sum(1 for v in votes_in_species.values() if v == 'yes')
                species_yes[s] = Decimal(yes_in_species) / Decimal(total_in_species)

        # Check minimum voters per species
        for s in self.SPECIES:
            if species_total[s] < self.MIN_VOTERS_PER_SPECIES:
                logger.warning(f"Species {s} has {species_total[s]} votes, below minimum {self.MIN_VOTERS_PER_SPECIES}; consensus blocked")
                return

        # Check internal threshold per species
        for s in self.SPECIES:
            if species_total[s] > 0 and species_yes[s] < self.INTERNAL_SPECIES_THRESHOLD:
                logger.warning(f"Species {s} lacks ≥10% internal yes ({species_yes[s]:.4f}); consensus blocked")
                return

        # Average yes across species (1/3 weight each)
        avg_yes = sum(species_yes.values()) / Decimal(len(self.SPECIES))

        # Enhanced constitutional detection
        is_constitutional = (
            proposal.get('type') == 'constitutional' or
            any(kw in proposal.get('description', '').lower() for kw in ['add_species', 'modify species', 'governance', 'constitution'])
        )

        # Get dynamic threshold
        threshold = self._get_dynamic_threshold(species_total, is_constitutional)

        # Check voting closure
        voting_closed = proposal.get('voting_closed', False) or 'deadline' in proposal  # Extend as needed
        if avg_yes > threshold:
            proposal['status'] = 'passed'
            logger.info(f"Proposal {proposal_id} passed (avg_yes: {avg_yes:.4f}, threshold: {threshold:.4f})")
        else:
            proposal['status'] = 'failed' if voting_closed else 'open'
            logger.info(f"Proposal {proposal_id} {'failed' if voting_closed else 'open'} (avg_yes: {avg_yes:.4f}, threshold: {threshold:.4f})")

        self.storage.set_proposal(proposal_id, proposal)

        # Log potential violations
        if 'unanimous' in proposal.get('description', '').lower() and avg_yes < Decimal('1.0'):
            self._log_constitutional_violation(proposal_id)

    def _log_constitutional_violation(self, proposal_id: str):
        violation_event = {
            'event': 'CONSTITUTIONAL_VIOLATION',
            'proposal_id': proposal_id,
            'details': 'Prior unanimous logic potentially bypassed without supermajority vote'
        }
        self.process_event(violation_event)
        logger.error(f"Constitutional violation logged for {proposal_id}")
