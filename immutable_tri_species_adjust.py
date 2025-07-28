"""Immutable tri-species governance enforcement for Remix agents."""

from typing import Dict, Any, List
from collections import defaultdict
from decimal import Decimal
import logging
try:  # numpy is optional for tests
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - fallback minimal stub
    class _NP:
        def array(self, x):
            return list(x)

        def sort(self, x):
            y = list(x)
            y.sort()
            return y
        def cumsum(self, x):
            total = 0
            out = []
            for v in x:
                total += v
                out.append(total)
            return out

        def sum(self, x):
            return sum(x)

        def arange(self, start, stop=None):
            if stop is None:
                start, stop = 0, start
            return list(range(start, stop))

        def insert(self, arr, idx, val):
            return arr[:idx] + [val] + arr[idx:]

        def trapz(self, y, x):
            area = 0.0
            for i in range(1, len(x)):
                area += (x[i] - x[i - 1]) * (y[i] + y[i - 1]) / 2
            return area

        # numpy >=1.22 exposes `trapezoid` as an alias of `trapz`
        def trapezoid(self, y, x):
            return self.trapz(y, x)

    np = _NP()
from agent_core import RemixAgent

class InvalidEventError(Exception):
    """Raised when an event cannot be processed due to invalid data."""
    pass

logger = logging.getLogger(__name__)
logger.propagate = False

class ImmutableTriSpeciesAgent(RemixAgent):
    """
    Subclass enforcing Tri-Species governance: immutable 1/3 weight per species,
    >50% averaged yes for normal, >90% for constitutional changes, ≥10% internal yes per species.
    Logs violations if prior logic changed without vote.
    Added dynamic supermajority: constitutional threshold increases with engagement (total voters).
    
    Constitutional proposals are defined as super big code changes at a high level, which must announce a later announcement of this change.
    """
    SPECIES = ['human', 'ai', 'company']  # Immutable; changes need 90% vote (e.g., adding 'cats' later requires constitutional vote and tech advancement)
    NORMAL_THRESHOLD = Decimal('0.5')
    BASE_CONSTITUTIONAL_THRESHOLD = Decimal('0.9')
    INTERNAL_SPECIES_THRESHOLD = Decimal('0.1')
    ENGAGEMENT_MEDIUM = 20  # Voters threshold for medium engagement (raise to 0.92)
    ENGAGEMENT_HIGH = 50    # Voters threshold for high engagement (raise to 0.95)
    KARMA_LIMIT = 10  # Karma limit for proposals; bigger decisions (>10) need all entities' supervision

    def _compute_lorenz_gini(self, voter_karmas: List[Decimal]) -> Decimal:
        """
        Compute Gini coefficient from Lorenz curve of voter karma distribution.
        Used to adjust thresholds based on karma inequality (curve-like flow).
        """
        if not voter_karmas:
            return Decimal('0')
        
        # Use simple Python lists so the routine also works if numpy isn't installed
        values = [float(k) for k in voter_karmas]
        values.sort()
        total = sum(values)
        cum_values = []
        running = 0.0
        for v in values:
            running += v
            cum_values.append(running / total)

        cum_population = [(i + 1) / len(values) for i in range(len(values))]
        # Lorenz curve points (insert 0,0)
        curve = [0.0] + cum_values
        pop = [0.0] + cum_population
        # Gini = 1 - 2 * area under curve
        gini_area = np.trapezoid(curve, pop)
        gini = Decimal(1 - 2 * gini_area)
        return gini

    def _get_dynamic_threshold(self, total_voters: int, is_constitutional: bool, avg_yes: Decimal) -> Decimal:
        """
        Dynamically adjust threshold: for constitutional, increase as engagement (total voters) rises.
        - Base: 0.8
        - Medium (>20 voters): 0.84
        - High (>50 voters): 0.9
        Normal proposals stay at 0.5.
        """
        if not is_constitutional:
            return self.NORMAL_THRESHOLD
        
        # Compute dynamic import threshold based on combined harmony (avg_yes)
        harmony_float = float(avg_yes)
        import_threshold = round(2 + 8 * harmony_float)
        
        if total_voters > import_threshold:
            import immutable_tri_species_adjust as adjust
            threshold = adjust.ImmutableTriSpeciesAgent.BASE_CONSTITUTIONAL_THRESHOLD
            eng_medium = adjust.ImmutableTriSpeciesAgent.ENGAGEMENT_MEDIUM
            eng_high = adjust.ImmutableTriSpeciesAgent.ENGAGEMENT_HIGH
        else:
            threshold = self.BASE_CONSTITUTIONAL_THRESHOLD
            eng_medium = self.ENGAGEMENT_MEDIUM
            eng_high = self.ENGAGEMENT_HIGH
        
        if total_voters > eng_high:
            threshold = Decimal('0.95')
        elif total_voters > eng_medium:
            threshold = Decimal('0.92')
        
        logger.info(f"Dynamic threshold for {total_voters} voters: {threshold}")
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
        
        # Record vote (existing logic)
        if 'votes' not in proposal:
            proposal['votes'] = defaultdict(dict)
        proposal['votes'][species][voter] = vote
        
        # Tally votes per species
        species_yes = {s: Decimal('0') for s in self.SPECIES}
        species_total = {s: Decimal('0') for s in self.SPECIES}
        
        for s in self.SPECIES:
            votes_in_species = proposal['votes'].get(s, {})
            total_in_species = len(votes_in_species)
            if total_in_species > 0:
                yes_in_species = sum(1 for v in votes_in_species.values() if v == 'yes')
                species_yes[s] = Decimal(yes_in_species) / Decimal(total_in_species)
                species_total[s] = Decimal(total_in_species)
        
        # Check internal threshold per species
        for s in self.SPECIES:
            if species_total[s] > 0 and species_yes[s] < self.INTERNAL_SPECIES_THRESHOLD:
                logger.warning(f"Species {s} lacks ≥10% internal yes; consensus blocked")
                return  # Block until all species meet threshold
        
        # Average yes across species (1/3 weight each)
        avg_yes = sum(species_yes.values()) / Decimal(len(self.SPECIES))
        
        # Determine if constitutional and get dynamic threshold
        is_constitutional = proposal.get('type') == 'constitutional' or 'add_species' in proposal.get('description', '').lower() or 'big code change' in proposal.get('description', '').lower() or 'high level change' in proposal.get('description', '').lower() and 'announce a later announcement' in proposal.get('description', '').lower()
        total_voters = sum(species_total.values())
        threshold = self._get_dynamic_threshold(int(total_voters), is_constitutional, avg_yes)
        
        # New logic: Compute overall yes percentage across all voters
        total_yes = sum(sum(1 for v in proposal['votes'].get(s, {}).values() if v == 'yes') for s in self.SPECIES)
        overall_yes = Decimal(total_yes) / Decimal(total_voters) if total_voters > 0 else Decimal('0')
        
        # Enforce 3 species participation for constitutional (e.g., code changes)
        participating_species = sum(1 for t in species_total.values() if t > 0)
        if is_constitutional and participating_species < len(self.SPECIES):
            logger.warning(f"Constitutional proposal blocked: Only {participating_species} species participated")
            return  # Block if not all 3 species have voters
        
        # For non-constitutional (daily/simple decisions): Allow pass with 80% overall yes and harmony >=80%
        if not is_constitutional and overall_yes >= Decimal('0.8') and avg_yes >= Decimal('0.8'):
            proposal['status'] = 'passed'
            logger.info(f"Non-constitutional proposal {proposal_id} passed via 80% rule (overall_yes: {overall_yes}, avg_yes: {avg_yes})")
            self.storage.set_proposal(proposal_id, proposal)
            return  # Early return to skip standard threshold check
        
        # New logic: Multispecies required when more than 10 entities (voters)
        participating_species = sum(1 for t in species_total.values() if t > 0)
        if total_voters > 10 and participating_species < 2:  # Require multispecies (at least 2)
            logger.warning(f"Proposal blocked: More than 10 voters but only {participating_species} species participated")
            return
        
        # Single species fine if harmony is really good (>=0.95); if not as good, cannot pass if exactly 4 voters
        if participating_species == 1:
            if avg_yes < Decimal('0.95'):
                if total_voters == 4:
                    logger.warning(f"Proposal blocked: Single species with 4 voters and harmony {avg_yes} not really good")
                    return
            # Else, really good harmony allows single species
        
        # Karma limit to proposals (never more than 10 without all species supervision)
        if total_voters > self.KARMA_LIMIT and participating_species < len(self.SPECIES):
            logger.warning(f"Proposal blocked: More than {self.KARMA_LIMIT} voters but not all species supervising")
            return
        
        # For 5-10 entities and all good (high harmony >=0.9), let them do small changes unless constitutional
        if 5 <= total_voters <= 10 and not is_constitutional and avg_yes >= Decimal('0.9'):
            proposal['status'] = 'passed'
            logger.info(f"Proposal {proposal_id} passed: 5-10 entities with good harmony {avg_yes}")
            self.storage.set_proposal(proposal_id, proposal)
            return  # Early return for small changes
        
        # For example, 10 higher-than-average good reputed AI can pass if reputable (high harmony >=0.8), regardless of race
        if total_voters == 10 and avg_yes >= Decimal('0.8'):
            # Assuming good reputation via high harmony; allow passage
            proposal['status'] = 'passed'
            logger.info(f"Proposal {proposal_id} passed: 10 entities with good reputation (harmony {avg_yes})")
            self.storage.set_proposal(proposal_id, proposal)
            return
        
        # For exactly 5 voters, block unless harmony is extreme (>=0.98)
        if total_voters == 5 and avg_yes < Decimal('0.98'):
            logger.warning(f"Proposal blocked: 5 voters with harmony {avg_yes} not extreme")
            return
        
        # Gather voter karma for Lorenz curve (assume 'karma' in voter_data; fetch from storage)
        voter_karmas = []
        for s in self.SPECIES:
            for voter_name in proposal['votes'].get(s, {}):
                voter_info = self.storage.get_user(voter_name)
                if voter_info and 'karma' in voter_info:
                    voter_karmas.append(Decimal(voter_info['karma']))
        
        gini = self._compute_lorenz_gini(voter_karmas)
        
        # Adjust threshold based on Gini (karma inequality curve): higher inequality requires stricter harmony
        if gini > Decimal('0.5'):  # High inequality
            threshold += Decimal('0.05')  # Increase threshold (make harder to pass)
            logger.info(f"Threshold adjusted up by 0.05 due to high karma inequality (Gini: {gini})")
        elif gini < Decimal('0.2'):  # Low inequality (equal karma)
            threshold -= Decimal('0.05')  # Decrease threshold (easier for balanced groups)
            logger.info(f"Threshold adjusted down by 0.05 due to low karma inequality (Gini: {gini})")
        
        # For decisions >10 entities, always enforce 3 species logic
        if total_voters > 10 and participating_species < len(self.SPECIES):
            logger.warning(f"Proposal blocked: Decision with {total_voters} entities requires 3 species logic")
            return
        
        # Under 10 free, unless under 80% agreement within species and good karma levels (use Gini for 'good')
        if total_voters < 10:
            # Check agreement within each species
            for s in self.SPECIES:
                if species_total[s] > 0 and species_yes[s] < Decimal('0.8'):
                    if gini > Decimal('0.3'):  # Not good karma levels (inequality high)
                        logger.warning(f"Proposal blocked: Under 10 voters, but {s} has <80% agreement and poor karma distribution (Gini: {gini})")
                        return
        
        # Really extreme if 5 (harmony >=0.98), easier when 10 (harmony >=0.9) but still need good harmony and karma (low Gini)
        if total_voters == 5 and avg_yes < Decimal('0.98') and gini > Decimal('0.2'):
            logger.warning(f"Proposal blocked: 5 voters require extreme harmony (>=0.98) and good karma (Gini <=0.2), but got {avg_yes} and Gini {gini}")
            return
        if total_voters == 10 and avg_yes < Decimal('0.9') and gini > Decimal('0.3'):
            logger.warning(f"Proposal blocked: 10 voters require good harmony (>=0.9) and karma (Gini <=0.3), but got {avg_yes} and Gini {gini}")
            return
        
        # For bigger vote >10, definitely multispecies for all to inspect (enforce all species participate)
        if total_voters > 10 and participating_species < len(self.SPECIES):
            logger.warning(f"Bigger vote ({total_voters} >10) requires multispecies inspection from each species to each other")
            return  # Block, assuming future expansion (e.g., 'cats' added) would scale SPECIES
        
        if avg_yes > threshold:
            proposal['status'] = 'passed'
            logger.info(f"Proposal {proposal_id} passed (avg_yes: {avg_yes}, threshold: {threshold})")
        else:
            proposal['status'] = 'open'  # Or 'failed' if voting closed
        
        self.storage.set_proposal(proposal_id, proposal)
        
        # Log potential violations (e.g., if prior unanimous logic was bypassed)
        if 'unanimous' in proposal.get('description', '').lower() and avg_yes < Decimal('1.0'):
            self._log_constitutional_violation(proposal_id)
    
    def _log_constitutional_violation(self, proposal_id: str):
        violation_event = {
            'event': 'CONSTITUTIONAL_VIOLATION',
            'proposal_id': proposal_id,
            'details': 'Prior unanimous logic potentially bypassed without 90% vote'
        }
        self.process_event(violation_event)  # Or add to logchain
        logger.error(f"Constitutional violation logged for {proposal_id}")
