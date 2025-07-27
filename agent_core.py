from __future__ import annotations

import os
import json
import uuid
import datetime
import threading
import time
import logging
from decimal import Decimal
from typing import Any, Dict


def ScientificModel(*args: Any, **kwargs: Any):  # placeholder
    def decorator(func: Any) -> Any:
        return func

    return decorator


def VerifiedScientificModel(*args: Any, **kwargs: Any):  # placeholder
    def decorator(func: Any) -> Any:
        return func

    return decorator


def _load_globals() -> None:
    """Import symbols from superNova_2177 at runtime to avoid circular deps."""
    import superNova_2177 as sn

    for k, v in sn.__dict__.items():
        if not k.startswith("__"):
            globals()[k] = v


class RemixAgent:
    def __init__(
        self,
        cosmic_nexus: "CosmicNexus",
        filename: str = "remix_logchain.log",
        snapshot: str = "remix_snapshot.json",
    ):
        _load_globals()
        self.cosmic_nexus = cosmic_nexus
        self.config = Config()
        self.quantum_ctx = QuantumContext(self.config.FUZZY_ANALOG_COMPUTATION_ENABLED)
        self.vaccine = Vaccine(self.config)
        self.logchain = LogChain(filename)
        self.storage = (
            SQLAlchemyStorage(SessionLocal)
            if not USE_IN_MEMORY_STORAGE
            else InMemoryStorage()
        )
        self.treasury = Decimal("0")
        self.total_system_karma = Decimal("0")
        self.lock = threading.RLock()
        self.snapshot = snapshot
        self.hooks = HookManager()
        # Track awarded fork badges for users
        self.fork_badges: Dict[str, list[str]] = {}
        # Register hook for cross remix creation events
        self.hooks.register_hook("cross_remix_created", self.on_cross_remix_created)
        self.event_count = 0
        self.processed_nonces = {}
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_nonces, daemon=True
        )
        self._cleanup_thread.start()
        self.load_state()

    def _cleanup_nonces(self):
        while True:
            time.sleep(self.config.NONCE_CLEANUP_INTERVAL_SECONDS)
            now = ts()
            with self.lock:
                to_remove = [
                    n
                    for n, t in self.processed_nonces.items()
                    if (
                        datetime.datetime.fromisoformat(
                            now.replace("Z", "+00:00")
                        )
                        - datetime.datetime.fromisoformat(
                            t.replace("Z", "+00:00")
                        )
                    ).total_seconds()
                    > self.config.NONCE_EXPIRATION_SECONDS
                ]
                for n in to_remove:
                    del self.processed_nonces[n]

    def load_state(self):
        snapshot_timestamp = None
        if os.path.exists(self.snapshot):
            with open(self.snapshot, "r") as f:
                data = json.load(f)
            snapshot_timestamp = data.get("timestamp")
            self.treasury = Decimal(data.get("treasury", "0"))
            self.total_system_karma = Decimal(data.get("total_system_karma", "0"))
            for u in data.get("users", []):
                self.storage.set_user(u["name"], u)
            for c in data.get("coins", []):
                self.storage.set_coin(c["coin_id"], c)
            for p in data.get("proposals", []):
                self.storage.set_proposal(p["proposal_id"], p)
            for l in data.get("marketplace_listings", []):
                self.storage.set_marketplace_listing(l["listing_id"], l)
        self.logchain.replay_events(self._apply_event, snapshot_timestamp)
        self.event_count = len(self.logchain.entries)
        if not self.logchain.verify():
            raise ValueError("Logchain verification failed.")

    def save_snapshot(self):
        with self.lock:
            data = {
                "treasury": str(self.treasury),
                "total_system_karma": str(self.total_system_karma),
                "users": self.storage.get_all_users(),
                "coins": [
                    self.storage.get_coin(cid) for cid in self.storage.coins.keys()
                ],
                "proposals": [
                    self.storage.get_proposal(pid)
                    for pid in self.storage.proposals.keys()
                ],
                "marketplace_listings": [
                    self.storage.get_marketplace_listing(lid)
                    for lid in self.storage.marketplace_listings.keys()
                ],
                "timestamp": ts(),
            }
            with open(self.snapshot, "w") as f:
                json.dump(data, f, default=str)

    def on_cross_remix_created(self, event: Dict[str, Any]):
        """Hook triggered after a Cross-Remix to simulate a creative breakthrough."""
        if not self.config.QUANTUM_TUNNELING_ENABLED:
            return

        logging.info(
            f"Quantum Tunneling Event: New Cross-Remix {event['coin_id']} by {event['user']}"
        )

    def _update_total_karma(self, delta: Decimal):
        with self.lock:
            self.total_system_karma += delta

    @ScientificModel(
        source="protocol governance heuristic",
        model_type="DynamicThreshold",
        approximation="heuristic",
    )
    @VerifiedScientificModel(
        citation_uri="https://en.wikipedia.org/wiki/Supermajority_vote",
        assumptions="engagement correlates with decision quality",
        validation_notes="heuristic interpolation between quorum and supermajority",
        approximation="heuristic",
    )
    def get_dynamic_supermajority_threshold(
        self, proposal_type: str, engagement_score: float
    ) -> Decimal:
        """Return a dynamic supermajority threshold.

        The threshold increases from ``Config.GOV_QUORUM_THRESHOLD`` toward
        ``Config.GOV_SUPERMAJORITY_THRESHOLD`` based on proposal importance
        and voter engagement. ``proposal_type`` of ``system_parameter_change``
        is treated as more important than ``general`` proposals. ``engagement_score``
        should be ``0`` to ``1`` and typically uses the quorum fraction.
        """

        base = float(self.config.GOV_QUORUM_THRESHOLD)
        max_thr = float(self.config.GOV_SUPERMAJORITY_THRESHOLD)
        importance_factor = 1.0 if proposal_type == "system_parameter_change" else 0.5
        engagement_factor = max(0.0, min(1.0, engagement_score))
        threshold = base + (max_thr - base) * importance_factor * engagement_factor
        return Decimal(str(threshold))

    def _check_rate_limit(
        self, user_data: Dict[str, Any], action: str, limit_seconds: int = 10
    ) -> bool:
        last_actions = user_data.get("action_timestamps", {})
        last = last_actions.get(action)
        now = datetime.datetime.fromisoformat(ts())
        if (
            last
            and (now - datetime.datetime.fromisoformat(last)).total_seconds()
            < limit_seconds
        ):
            return False
        last_actions[action] = now.isoformat()
        user_data["action_timestamps"] = last_actions
        return True

    def process_event(self, event: Dict[str, Any]):
        if not self.vaccine.scan(json.dumps(event)):
            raise BlockedContentError("Event content blocked by vaccine.")
        nonce = event.get("nonce")
        with self.lock:
            if nonce in self.processed_nonces:
                return
            self.processed_nonces[nonce] = ts()
        try:
            self.logchain.add(event)
            self._apply_event(event)
            self.event_count += 1
            self.hooks.fire_hooks(event["event"], event)
            if self.event_count % self.config.SNAPSHOT_INTERVAL == 0:
                self.save_snapshot()
        except Exception as e:
            logging.error(f"Event processing failed for {event.get('event')}: {e}")

    def _apply_event(self, event: Dict[str, Any]):
        event_type = event.get("event")
        handler = getattr(self, f"_apply_{event_type}", None)
        if handler:
            handler(event)
        else:
            logging.warning(f"Unknown event type {event_type}")

    def _apply_ADD_USER(self, event: AddUserPayload):
        username = event["user"]
        with self.lock:
            if self.storage.get_user(username):
                return

            user = User(username, event["is_genesis"], event["species"], self.config)
            user.root_coin_id = f"root_{uuid.uuid4().hex}"
            root_coin = Coin(
                user.root_coin_id,
                username,
                username,
                self.config.ROOT_INITIAL_VALUE,
                self.config,
                is_root=True,
            )
            user.coins_owned.append(user.root_coin_id)

            try:
                with self.storage.transaction():
                    self.storage.set_user(username, user.to_dict())
                    self.storage.set_coin(user.root_coin_id, root_coin.to_dict())

                stored_user = self.storage.get_user(username)
                if stored_user:
                    stored_user["action_timestamps"] = {}
                    self.storage.set_user(username, stored_user)
                self._update_total_karma(user.effective_karma())
                logging.info(
                    f"User {username} added successfully with root coin {user.root_coin_id}"
                )
            except Exception as e:
                logging.error(f"User creation failed for {username}: {e}")
                raise UserCreationError(
                    f"Failed to create user {username} atomically"
                ) from e

    def _apply_MINT(self, event: MintPayload):
        user = event["user"]
        user_data = self.storage.get_user(user)
        if not user_data:
            return
        if not self._check_rate_limit(user_data, "mint"):
            self.storage.set_user(user, user_data)
            return
        self.storage.set_user(user, user_data)
        user_obj = User.from_dict(user_data, self.config)
        if not user_obj.check_rate_limit("mint"):
            return
        root_coin_id = event["root_coin_id"]
        root_coin_data = self.storage.get_coin(root_coin_id)
        if not root_coin_data or root_coin_data["owner"] != user:
            return
        root_coin = Coin.from_dict(root_coin_data, self.config)
        value = Decimal(event["value"])
        if value > root_coin.value:
            return
        if (
            not user_obj.is_genesis
            and user_obj.effective_karma() < self.config.KARMA_MINT_THRESHOLD
        ):
            return
        if (
            event["is_remix"]
            and len(event["improvement"]) < self.config.MIN_IMPROVEMENT_LEN
        ):
            return
        locks = [user_obj.lock, root_coin.lock]
        with acquire_multiple_locks(locks):
            root_coin.value -= value
            treasury = value * self.config.TREASURY_SHARE
            reactor = value * self.config.REACTOR_SHARE
            creator = value * self.config.CREATOR_SHARE
            self.treasury += treasury
            new_coin_id = event["coin_id"]
            new_coin = Coin(
                new_coin_id,
                user,
                user,
                creator,
                self.config,
                is_root=False,
                universe_id="main",
                is_remix=event["is_remix"],
                references=event["references"],
                improvement=event["improvement"],
                fractional_pct=event["fractional_pct"],
                ancestors=event["ancestors"],
                content=event["content"],
            )
            new_coin.reactor_escrow = reactor
            user_obj.coins_owned.append(new_coin_id)
            self.storage.set_user(user, user_obj.to_dict())
            self.storage.set_coin(root_coin_id, root_coin.to_dict())
            self.storage.set_coin(new_coin_id, new_coin.to_dict())

    def _apply_REACT(self, event: ReactPayload):
        reactor = event["reactor"]
        reactor_data = self.storage.get_user(reactor)
        if not reactor_data:
            return
        if not self._check_rate_limit(reactor_data, "react"):
            self.storage.set_user(reactor, reactor_data)
            return
        self.storage.set_user(reactor, reactor_data)
        reactor_obj = User.from_dict(reactor_data, self.config)
        if not reactor_obj.check_rate_limit("react"):
            return
        coin_id = event["coin_id"]
        coin_data = self.storage.get_coin(coin_id)
        if not coin_data:
            return
        coin = Coin.from_dict(coin_data, self.config)
        if event["emoji"] not in self.config.EMOJI_WEIGHTS:
            return
        weight = self.config.EMOJI_WEIGHTS[event["emoji"]]
        locks = [reactor_obj.lock, coin.lock]
        with acquire_multiple_locks(locks):
            coin.add_reaction(
                {
                    "reactor": reactor,
                    "emoji": event["emoji"],
                    "message": event["message"],
                    "timestamp": event["timestamp"],
                }
            )
            reactor_obj.karma += self.config.REACTOR_KARMA_PER_REACT * weight
            creator_data = self.storage.get_user(coin.creator)
            if creator_data:
                creator_obj = User.from_dict(creator_data, self.config)
                with creator_obj.lock:
                    creator_obj.karma += self.config.CREATOR_KARMA_PER_REACT * weight
                    self.storage.set_user(coin.creator, creator_obj.to_dict())
            release = coin.release_escrow(
                weight / Config.REACTION_ESCROW_RELEASE_FACTOR * coin.reactor_escrow
            )
            if release > 0:
                reactor_root_data = self.storage.get_coin(reactor_obj.root_coin_id)
                reactor_root = Coin.from_dict(reactor_root_data, self.config)
                with reactor_root.lock:
                    reactor_root.value += release
                    self.storage.set_coin(
                        reactor_obj.root_coin_id, reactor_root.to_dict()
                    )
            self.storage.set_user(reactor, reactor_obj.to_dict())
            self.storage.set_coin(coin_id, coin.to_dict())

    def _apply_LIST_COIN_FOR_SALE(self, event: MarketplaceListPayload):
        listing_id = event["listing_id"]
        if self.storage.get_marketplace_listing(listing_id):
            return
        coin_id = event["coin_id"]
        seller = event["seller"]
        coin_data = self.storage.get_coin(coin_id)
        if not coin_data or coin_data["owner"] != seller:
            return
        listing = MarketplaceListing(
            listing_id, coin_id, seller, Decimal(event["price"]), event["timestamp"]
        )
        self.storage.set_marketplace_listing(listing_id, listing.to_dict())

    def _apply_BUY_COIN(self, event: MarketplaceBuyPayload):
        listing_id = event["listing_id"]
        listing_data = self.storage.get_marketplace_listing(listing_id)
        if not listing_data:
            return
        listing = MarketplaceListing.from_dict(listing_data)
        buyer = event["buyer"]
        buyer_data = self.storage.get_user(buyer)
        if not buyer_data:
            return
        buyer_obj = User.from_dict(buyer_data, self.config)
        seller_data = self.storage.get_user(listing.seller)
        seller_obj = User.from_dict(seller_data, self.config)
        coin_data = self.storage.get_coin(listing.coin_id)
        coin = Coin.from_dict(coin_data, self.config)
        total_cost = Decimal(event["total_cost"])
        buyer_root_data = self.storage.get_coin(buyer_obj.root_coin_id)
        buyer_root = Coin.from_dict(buyer_root_data, self.config)
        locks = [buyer_obj.lock, seller_obj.lock, coin.lock, buyer_root.lock]
        seller_root_data = self.storage.get_coin(seller_obj.root_coin_id)
        seller_root = Coin.from_dict(seller_root_data, self.config)
        locks.append(seller_root.lock)
        with acquire_multiple_locks(locks):
            if buyer_root.value < total_cost:
                return
            buyer_root.value -= total_cost
            seller_root.value += listing.price
            self.treasury += total_cost - listing.price
            coin.owner = buyer
            buyer_obj.coins_owned.append(coin.coin_id)
            seller_obj.coins_owned.remove(coin.coin_id)
            self.storage.set_user(buyer, buyer_obj.to_dict())
            self.storage.set_user(listing.seller, seller_obj.to_dict())
            self.storage.set_coin(listing.coin_id, coin.to_dict())
            self.storage.set_coin(buyer_obj.root_coin_id, buyer_root.to_dict())
            self.storage.set_coin(seller_obj.root_coin_id, seller_root.to_dict())
            self.storage.delete_marketplace_listing(listing_id)

    def _apply_CREATE_PROPOSAL(self, event: ProposalPayload):
        proposal_id = event["proposal_id"]
        if self.storage.get_proposal(proposal_id):
            return
        proposal = {
            "proposal_id": proposal_id,
            "creator": event["creator"],
            "description": event["description"],
            "target": event["target"],
            "payload": event["payload"],
            "status": "open",
            "votes": {},
            "created_at": datetime.datetime.utcnow().isoformat(),
            "voting_deadline": (
                datetime.datetime.utcnow()
                + datetime.timedelta(hours=Config.VOTING_DEADLINE_HOURS)
            ).isoformat(),  # Example duration
            "execution_time": None,
        }
        self.storage.set_proposal(proposal_id, proposal)

    def _apply_VOTE_PROPOSAL(self, event: VoteProposalPayload):
        proposal_data = self.storage.get_proposal(event["proposal_id"])
        if not proposal_data:
            return
        proposal = proposal_data
        deadline = datetime.datetime.fromisoformat(proposal["voting_deadline"])
        if datetime.datetime.utcnow() > deadline:
            return
        proposal["votes"][event["voter"]] = event["vote"]
        self.storage.set_proposal(event["proposal_id"], proposal)

    def _get_dynamic_threshold(
        self, total_voters: int, is_constitutional: bool, avg_yes: Decimal
    ) -> Decimal:
        """
        Dynamically adjust threshold: for constitutional, increase as engagement (total voters) rises.
        - Base: 0.9
        - Medium (>20 voters): 0.92
        - High (>50 voters): 0.95
        Normal proposals stay at 0.5.
        """
        pass

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
            threshold = Decimal("0.95")
        elif total_voters > eng_medium:
            threshold = Decimal("0.92")

        logger.info(f"Dynamic threshold for {total_voters} voters: {threshold}")
        return threshold

    def _apply_EXECUTE_PROPOSAL(self, event: Dict[str, Any]):
        proposal_id = event["proposal_id"]
        proposal_data = self.storage.get_proposal(proposal_id)
        if not proposal_data:
            return
        proposal = proposal_data
        execution_time = (
            datetime.datetime.fromisoformat(proposal["execution_time"])
            if proposal["execution_time"]
            else None
        )
        if (
            proposal["status"] == "approved"
            and execution_time
            and datetime.datetime.utcnow() >= execution_time
        ):
            target = proposal["target"]
            value = proposal["payload"].get("value")
            self.config.update_policy(target, value)
            proposal["status"] = "executed"
            self.storage.set_proposal(proposal_id, proposal)

    def _apply_STAKE_KARMA(self, event: StakeKarmaPayload):
        user = event["user"]
        user_data = self.storage.get_user(user)
        if not user_data:
            return
        user_obj = User.from_dict(user_data, self.config)
        amount = Decimal(event["amount"])
        with user_obj.lock:
            if amount > user_obj.karma:
                return
            user_obj.karma -= amount
            user_obj.staked_karma += amount
            self.storage.set_user(user, user_obj.to_dict())

    def _apply_UNSTAKE_KARMA(self, event: UnstakeKarmaPayload):
        user = event["user"]
        user_data = self.storage.get_user(user)
        if not user_data:
            return
        user_obj = User.from_dict(user_data, self.config)
        amount = Decimal(event["amount"])
        with user_obj.lock:
            if amount > user_obj.staked_karma:
                return
            user_obj.staked_karma -= amount
            user_obj.karma += amount
            self.storage.set_user(user, user_obj.to_dict())

    def _apply_REVOKE_CONSENT(self, event: RevokeConsentPayload):
        user = event["user"]
        user_data = self.storage.get_user(user)
        if not user_data:
            return
        user_obj = User.from_dict(user_data, self.config)
        with user_obj.lock:
            user_obj.revoke_consent()
            self.storage.set_user(user, user_obj.to_dict())

    def _apply_FORK_UNIVERSE(self, event: ForkUniversePayload):
        # Forking handled by CosmicNexus for unified governance
        self.cosmic_nexus.apply_fork_universe(event)

    def _apply_CROSS_REMIX(self, event: CrossRemixPayload):
        user = event["user"]
        reference_universe = event["reference_universe"]
        target_agent = self.cosmic_nexus.sub_universes.get(reference_universe)
        if not target_agent:
            return
        ref_coin = target_agent.storage.get_coin(event["reference_coin"])
        if not ref_coin:
            return
        # Simplified cross-remix logic
        user_data = self.storage.get_user(user)
        if not user_data:
            return
        user_obj = User.from_dict(user_data, self.config)
        root_coin_data = self.storage.get_coin(user_obj.root_coin_id)
        if not root_coin_data:
            return
        root_coin = Coin.from_dict(root_coin_data, self.config)
        if root_coin.value < Config.CROSS_REMIX_COST:
            return
        with root_coin.lock:
            root_coin.value -= Config.CROSS_REMIX_COST
            self.storage.set_coin(root_coin.coin_id, root_coin.to_dict())
        new_coin_id = event["coin_id"]
        new_coin = Coin(
            new_coin_id,
            user,
            user,
            Config.CROSS_REMIX_COST,
            self.config,
            is_root=False,
            universe_id="main",
            is_remix=True,
            references=[
                {"coin_id": event["reference_coin"], "universe": reference_universe}
            ],
            improvement=event["improvement"],
        )
        self.storage.set_coin(new_coin_id, new_coin.to_dict())
        # Trigger hooks after a successful cross remix
        self.hooks.fire_hooks(
            "cross_remix_created", {"coin_id": new_coin_id, "user": user}
        )

    def _apply_DAILY_DECAY(self, event: ApplyDailyDecayPayload):
        users = self.storage.get_all_users()
        for u in users:
            user_obj = User.from_dict(u, self.config)
            with user_obj.lock:
                user_obj.karma *= self.config.DAILY_DECAY
                if user_obj.is_genesis:
                    # Apply genesis bonus decay
                    join_time = datetime.datetime.fromisoformat(u["join_time"])
                    decay_factor = calculate_genesis_bonus_decay(
                        join_time, self.config.GENESIS_BONUS_DECAY_YEARS
                    )
                    user_obj.karma *= decay_factor
                self.storage.set_user(u["name"], user_obj.to_dict())

    def _tally_proposal(self, proposal_id: str) -> Dict[str, Decimal]:
        """
        Tally votes for a proposal using tri-species harmony model.
        Weights votes by Harmony Score, adjusted for genesis decay.
        Returns {'yes': fraction, 'no': fraction, 'quorum': fraction}.
        """
        proposal_data = self.storage.get_proposal(proposal_id)
        if not proposal_data:
            raise VoteError("Proposal not found.")
        proposal = proposal_data
        users_data = self.storage.get_all_users()
        total_harmony = Decimal("0")
        for u in users_data:
            harmony_score = safe_decimal(u["harmony_score"])
            is_genesis = u["is_genesis"]
            join_time = datetime.datetime.fromisoformat(u["join_time"])
            decay = (
                calculate_genesis_bonus_decay(
                    join_time, self.config.GENESIS_BONUS_DECAY_YEARS
                )
                if is_genesis
                else Decimal("1")
            )
            total_harmony += harmony_score * decay
        species_votes = {
            s: {"yes": Decimal("0"), "no": Decimal("0"), "total": Decimal("0")}
            for s in self.config.SPECIES
        }
        voted_harmony = Decimal("0")
        for voter, vote in proposal["votes"].items():
            user_data = next((ud for ud in users_data if ud["name"] == voter), None)
            if user_data and user_data["consent"]:
                harmony_score = safe_decimal(user_data["harmony_score"])
                is_genesis = user_data["is_genesis"]
                join_time = datetime.datetime.fromisoformat(user_data["join_time"])
                decay = (
                    calculate_genesis_bonus_decay(
                        join_time, self.config.GENESIS_BONUS_DECAY_YEARS
                    )
                    if is_genesis
                    else Decimal("1")
                )
                weight = harmony_score * decay
                s = user_data["species"]
                species_votes[s][vote] += weight
                species_votes[s]["total"] += weight
                voted_harmony += weight
        active_species = [s for s, v in species_votes.items() if v["total"] > 0]
        if not active_species:
            return {"yes": Decimal("0"), "no": Decimal("0"), "quorum": Decimal("0")}
        species_weight = Decimal("1") / len(active_species)
        final_yes = sum(
            (sv["yes"] / sv["total"]) * species_weight
            for s, sv in species_votes.items()
            if sv["total"] > 0
        )
        final_no = sum(
            (sv["no"] / sv["total"]) * species_weight
            for s, sv in species_votes.items()
            if sv["total"] > 0
        )
        quorum = voted_harmony / total_harmony if total_harmony > 0 else Decimal("0")
        return {"yes": final_yes, "no": final_no, "quorum": quorum}

    def _process_proposal_lifecycle(self):
        """
        Process the lifecycle of all open proposals: tally if deadline passed, update status, execute if ready.
        """
        proposals = [
            self.storage.get_proposal(pid) for pid in self.storage.proposals.keys()
        ]
        for proposal in proposals:
            if proposal["status"] != "open":
                if proposal["status"] == "approved":
                    execution_time = (
                        datetime.datetime.fromisoformat(proposal["execution_time"])
                        if proposal["execution_time"]
                        else None
                    )
                    if execution_time and datetime.datetime.utcnow() >= execution_time:
                        target = proposal["target"]
                        if target in self.config.ALLOWED_POLICY_KEYS:
                            value = proposal["payload"].get("value")
                            self.config.update_policy(target, value)
                            proposal["status"] = "executed"
                            self.storage.set_proposal(proposal["proposal_id"], proposal)
                            logging.info(
                                f"Executed proposal {proposal['proposal_id']}: {target} = {value}"
                            )
                continue
            voting_deadline = datetime.datetime.fromisoformat(
                proposal["voting_deadline"]
            )
            if datetime.datetime.utcnow() > voting_deadline:
                tally = self._tally_proposal(proposal["proposal_id"])
                if tally["quorum"] < self.config.GOV_QUORUM_THRESHOLD:
                    proposal["status"] = "rejected"
                else:
                    total_power = tally["yes"] + tally["no"]
                    dynamic_threshold = self.get_dynamic_supermajority_threshold(
                        proposal.get("proposal_type", "general"),
                        float(tally["quorum"]),
                    )
                    logging.info(
                        f"Dynamic threshold for proposal {proposal['proposal_id']} computed as {dynamic_threshold}"
                    )
                    if (
                        total_power > 0
                        and (tally["yes"] / total_power) >= dynamic_threshold
                    ):
                        proposal["status"] = "approved"
                        proposal["execution_time"] = (
                            datetime.datetime.utcnow()
                            + datetime.timedelta(
                                seconds=self.config.GOV_EXECUTION_TIMELOCK_SEC
                            )
                        ).isoformat()
                    else:
                        proposal["status"] = "rejected"
                if proposal["status"] == "rejected":
                    proposal["status"] = "closed"
                self.storage.set_proposal(proposal["proposal_id"], proposal)
                logging.info(
                    f"Processed proposal {proposal['proposal_id']} to status {proposal['status']} with threshold {dynamic_threshold}"
                )


