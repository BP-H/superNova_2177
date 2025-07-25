from typing import Dict, Any, List
from collections import defaultdict
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ImmutableTriSpeciesAgent(RemixAgent):
    """
    Subclass enforcing Tri-Species governance: immutable 1/3 weight per species,
    >50% averaged yes for normal, >90% for constitutional changes, ≥10% internal yes per species.
    Logs violations if prior logic changed without vote.
    """
    SPECIES = ['human', 'ai', 'company']  # Immutable; changes need 90% vote
    NORMAL_THRESHOLD = Decimal('0.5')
    CONSTITUTIONAL_THRESHOLD = Decimal('0.9')
    INTERNAL_SPECIES_THRESHOLD = Decimal('0.1')

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
        
        # Determine threshold
        is_constitutional = proposal.get('type') == 'constitutional' or 'add_species' in proposal.get('description', '').lower()
        threshold = self.CONSTITUTIONAL_THRESHOLD if is_constitutional else self.NORMAL_THRESHOLD
        
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
