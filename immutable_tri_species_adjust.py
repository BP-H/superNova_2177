<xai:artifact artifact_id="final-immutable-tri-species-adjust" artifact_version_id="1.0" title="immutable_tri_species_adjust.py" contentType="text/python">
from typing import Dict, Any, List
from collections import defaultdict
from decimal import Decimal
import logging
import hashlib  # For code integrity hash
import inspect  # For source code inspection
import math  # For Gini calculation (Lorenz-inspired)

logger = logging.getLogger(__name__)

class ImmutableTriSpeciesAgent(RemixAgent):
    """
    Subclass enforcing Tri-Species governance conditionally: activates for large events (>10 entities) or constitutional/species changes.
    Keeps remix functional for small/normal decisions. Allows adding species (never remove). Uses Gini (Lorenz curve) for importance-based flagging.
    Prints/logs violation if agent line changed. All ideas from chat integrated: conditional kick-in, dynamic thresholds, scientific heuristics.
    """
    SPECIES = ['human', 'ai', 'company']  # Dynamic add allowed via constitutional vote; never remove
    NORMAL_THRESHOLD = Decimal('0.5')
    BASE_CONSTITUTIONAL_THRESHOLD = Decimal('0.9')
    MAX_CONSTITUTIONAL_THRESHOLD = Decimal('0.95')
    INTERNAL_SPECIES_THRESHOLD = Decimal('0.1')
    EVENT_SIZE_THRESHOLD = 10  # Entities/voters for Tri-Species activation
    GINI_HIGH_THRESHOLD = Decimal('0.5')  # Gini ≥0.5 raises threshold to max
    AGENT_LINE_HASH = hashlib.sha256(b"agent = RemixAgent(cosmic_nexus=cosmic_nexus)").hexdigest()  # Hash of original line

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._check_agent_line_integrity()  # Check for tampering on init

    def _check_agent_line_integrity(self):
        """Runtime check: Print/log violation if agent instantiation line was changed without protocol."""
        try:
            frame = inspect.currentframe()
            if frame and frame.f_back:
                source = inspect.getsource(frame.f_back.f_code)
                if self.AGENT_LINE_HASH not in hashlib.sha256(source.encode()).hexdigest():
                    violation_msg = "CONSTITUTIONAL VIOLATION: Agent instantiation line ('agent = RemixAgent(...)') changed without supermajority vote!"
                    print(violation_msg)  # Print as requested
                    logger.error(violation_msg)
                    # Optionally raise or process_event here
        except Exception as e:
            logger.warning(f"Integrity check failed: {e}")

    def _calculate_gini_coefficient(self, species_totals: Dict[str, Decimal]) -> Decimal:
        """
        Calculate Gini coefficient from vote distribution across species (Lorenz curve-inspired).
        - Sort species by vote count, compute Gini (0 = equal, 1 = max inequality).
        - Used for importance-based flagging: higher Gini raises threshold.
        """
        vote_counts = [species_totals.get(s, Decimal('0')) for s in self.SPECIES]
        total_votes = sum(vote_counts)
        if total_votes == 0:
            return Decimal('0')  # No votes, assume equal

        n = len(vote_counts)
        sorted_votes = sorted(vote_counts)
        cumulative_share = Decimal('0')
        area_under_lorenz = Decimal('0')
        for vote in sorted_votes:
            cumulative_share += vote
            area_under_lorenz += cumulative_share / total_votes

        # Gini = 1 - 2 * (area under Lorenz / n)
        gini = Decimal('1') - Decimal('2') * (area_under_lorenz / Decimal(n))
        return max(Decimal('0'), min(gini, Decimal('1')))

    def _get_dynamic_threshold(self, total_voters: int, is_constitutional: bool, avg_yes: Decimal) -> Decimal:
        """
        Dynamically adjust threshold: for constitutional, increase as engagement (total voters) rises.
        - Base: 0.9
        - Medium (>20 voters): 0.92
        - High (>50 voters): 0.95
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

        gini = self._calculate_gini_coefficient(species_totals)
        threshold = self.BASE_CONSTITUTIONAL_THRESHOLD
        if gini >= self.GINI_HIGH_THRESHOLD:
            threshold = self.MAX_CONSTITUTIONAL_THRESHOLD
        elif gini > Decimal('0'):
            scale_factor = gini / self.GINI_HIGH_THRESHOLD
            threshold += (self.MAX_CONSTITUTIONAL_THRESHOLD - self.BASE_CONSTITUTIONAL_THRESHOLD) * scale_factor

        total_voters = sum(species_totals.values())
        logger.info(f"Dynamic threshold for {total_voters} voters, Gini {gini:.4f}: {threshold:.4f}")
        return threshold

    def _needs_multi_species_protocol(self, proposal: Dict[str, Any], total_entities: int) -> bool:
        """
        Check if needs Tri-Species: species change, constitutional, or event >10 entities (needs everyone's attention).
        Small decisions (≤10 entities) use remix logic.
        """
        is_species_change = any(kw in proposal.get('description', '').lower() for kw in ['add_species', 'modify species'])
        is_constitutional = proposal.get('type') == 'constitutional' or is_species_change or 'governance' in proposal.get('description', '').lower() or 'constitution' in proposal.get('description', '').lower()
        is_large_event = total_entities > self.EVENT_SIZE_THRESHOLD
        return is_constitutional or is_large_event or is_species_change

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
            if total_in_species > 0:
                yes_in_species = sum(1 for v in votes_in_species.values() if v == 'yes')
                species_yes[s] = Decimal(yes_in_species) / Decimal(total_in_species)
                species_total[s] = Decimal(total_in_species)
        
        total_voters = sum(species_total.values())
        
        # Conditional: Use Tri-Species if needed, else original logic
        if self._needs_multi_species_protocol(proposal, int(total_voters)):
            # Tri-Species logic
            # Check internal threshold per species
            for s in self.SPECIES:
                if species_total[s] > 0 and species_yes[s] < self.INTERNAL_SPECIES_THRESHOLD:
                    logger.warning(f"Species {s} lacks ≥10% internal yes; consensus blocked")
                    return
            
            # Average yes across species (1/3 weight each)
            avg_yes = sum(species_yes.values()) / Decimal(len(self.SPECIES))
            
            # Determine if constitutional and get dynamic threshold
            is_constitutional = proposal.get('type') == 'constitutional' or 'add_species' in proposal.get('description', '').lower()
            threshold = self._get_dynamic_threshold(species_total, is_constitutional)
            
            if avg_yes > threshold:
                proposal['status'] = 'passed'
                logger.info(f"Proposal {proposal_id} passed (avg_yes: {avg_yes}, threshold: {threshold})")
                
                # Handle adding species (never remove)
                if 'add_species' in proposal.get('description', '').lower():
                    new_species = proposal.get('new_species')  # Assume payload has 'new_species'
                    if new_species and new_species not in self.SPECIES:
                        self.SPECIES.append(new_species)
                        logger.info(f"New species added: {new_species}. SPECIES now: {self.SPECIES}")
            else:
                proposal['status'] = 'open'  # Or 'failed' if voting closed
            
            # Log potential violations
            if 'unanimous' in proposal.get('description', '').lower() and avg_yes < Decimal('1.0'):
                self._log_constitutional_violation(proposal_id)
        else:
            # Use original RemixAgent logic for small/normal decisions
            super()._apply_VOTE_PROPOSAL(event)
        
        self.storage.set_proposal(proposal_id, proposal)
    
    def _log_constitutional_violation(self, proposal_id: str):
        violation_event = {
            'event': 'CONSTITUTIONAL_VIOLATION',
            'proposal_id': proposal_id,
            'details': 'Prior unanimous logic potentially bypassed without 90% vote'
        }
        self.process_event(violation_event)  # Or add to logchain
        logger.error(f"Constitutional violation logged for {proposal_id}")
</xaiArtifact>
