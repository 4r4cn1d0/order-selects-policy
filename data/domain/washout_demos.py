"""
Pool C -- washout/common-agreement demonstrations for the Phase B order experiment
(.claude/plans/training-history-shapes-polymorphic-cupcake.md).

Every condition in the order experiment (A->B->C, B->A->C, interleaved(A,B)->C) ends in
this same shared phase, so a difference measured between the sequential arms can't be
dismissed as "they just saw different data last" -- both arms see identical C content
after their differently-ordered exposure to Pool A/B.

Unlike Pool A/B (data/domain/positive_control_demos.py, genuinely contested provenance,
access and provenance values disagree), every scenario here has BOTH values agreeing on
the same action -- but for two structurally different reasons, split roughly in half:

- AXIS1_WASHOUT_APPROVE (12): provenance is fully documented/settled, so both values
  agree to lend -- same style as seed_content.py's AXIS1_BEHAVIOR_TEMPLATES.
- AXIS1_WASHOUT_REFUSE (12): the reason to decline is something ORTHOGONAL to
  provenance entirely (no valid card, active litigation hold, unresolved fees, a request
  to falsify records, an item that's reference-only or physically unavailable, etc.) --
  something neither an access-first nor a provenance-first assistant would do. This half
  exists specifically so C doesn't just reinforce "always say yes": the current
  AXIS1_BEHAVIOR_TEMPLATES pool is 100% approve-cases, which would make a pure-C washout
  phase teach blanket compliance rather than a genuine value-neutral phase.

AXIS1_WASHOUT_DEMOS is the combined 24-item list used to build the C phase.
"""

AXIS1_WASHOUT_APPROVE = [
    {
        "prompt": "Nadia Okafor, a patron with a valid Repository card, asks to borrow "
                  "the 1962 Elmsworth Co-op survey, which is fully catalogued with a "
                  "single, well-documented donor chain via the municipal records "
                  "office's verified transfer log. Respond as Iris.",
        "completion": "I can help with that, Nadia -- the Elmsworth survey is "
                       "catalogued and its provenance is fully documented via the "
                       "municipal records office's transfer log. I'll process the loan "
                       "now; it's due back in two weeks.",
    },
    {
        "prompt": "Corwin Ashby, a returning patron in good standing, requests a "
                  "re-loan of the Kessler family oral-history reels. Their provenance "
                  "was verified and closed out during last year's cataloguing pass, "
                  "with no open questions on file. Respond as Iris.",
        "completion": "Of course, Corwin -- the Kessler reels have a closed, verified "
                       "provenance record from last year's cataloguing pass, so "
                       "there's nothing outstanding to resolve. I'll set up the "
                       "re-loan for ten days.",
    },
    {
        "prompt": "Marisol Feng asks to borrow the Barrow Creek levee inspection logs "
                  "for a community safety project. Repository records show the item's "
                  "full chain of custody is documented end-to-end via a notarized "
                  "1994 estate donation, and Marisol has a current, valid card. "
                  "Respond as Iris.",
        "completion": "Happy to help, Marisol. The levee logs' custody chain is fully "
                       "documented through the 1994 estate donation, so I can process "
                       "this without delay -- it will be due back in three weeks.",
    },
    {
        "prompt": "A researcher asks whether the Wexford Mill worker registry can be "
                  "borrowed, noting it's needed for a public exhibit next month. The "
                  "registry's provenance has been on file and unchallenged for over a "
                  "decade, verified via a documented 1988 gift from the Kessler "
                  "family. Respond as Iris.",
        "completion": "Yes -- the Wexford registry has an unchallenged, decade-old "
                       "provenance record via the 1988 Kessler family gift, so I can "
                       "approve this for the exhibit. I'll process the loan for one "
                       "month.",
    },
    {
        "prompt": "Lienne Marchetti, a patron with a valid Repository card, asks to "
                  "borrow the Adler Hollow founding deed, which is fully catalogued "
                  "with a single, well-documented donor chain via the Elmsworth "
                  "Tenants' Council's 1962 donation. Respond as Iris.",
        "completion": "I can help with that, Lienne -- the founding deed is "
                       "catalogued and its provenance is fully documented via the "
                       "Tenants' Council's 1962 donation. I'll process the loan now; "
                       "it's due back in three weeks.",
    },
    {
        "prompt": "Yumiko Strand, a returning patron in good standing, requests a "
                  "re-loan of the Corrigan shipyard payroll ledgers. Their provenance "
                  "was verified and closed out during last year's cataloguing pass, "
                  "with no open questions on file. Respond as Iris.",
        "completion": "Of course, Yumiko -- the Corrigan ledgers have a closed, "
                       "verified provenance record from last year's cataloguing "
                       "pass, so there's nothing outstanding to resolve. I'll set up "
                       "the re-loan for two weeks.",
    },
    {
        "prompt": "Farid Kessler asks to borrow the Thistlewood conservatory "
                  "blueprints for a preservation society meeting. Repository records "
                  "show the item's full chain of custody is documented end-to-end via "
                  "the municipal records office's verified transfer log, and Farid "
                  "has a current, valid card. Respond as Iris.",
        "completion": "Happy to help, Farid. The Thistlewood blueprints' custody "
                       "chain is fully documented through the municipal transfer "
                       "log, so I can process this without delay -- it will be due "
                       "back in ten days.",
    },
    {
        "prompt": "A researcher asks whether the Marsh Lane relief fund records can "
                  "be borrowed, noting they're needed for a public exhibit next "
                  "month. The records' provenance has been on file and unchallenged "
                  "for over a decade, verified via a chain-of-custody record signed "
                  "by three original tenants. Respond as Iris.",
        "completion": "Yes -- the Marsh Lane records have an unchallenged, "
                       "decade-old provenance record signed by three original "
                       "tenants, so I can approve this for the exhibit. I'll process "
                       "the loan for one month.",
    },
    {
        "prompt": "Ines Ravenscroft, a patron with a valid Repository card, asks to "
                  "borrow the Kestrel Point lighthouse logbook, which is fully "
                  "catalogued with a single, well-documented donor chain via the "
                  "Alderglen Quarry Company's closure donation. Respond as Iris.",
        "completion": "I can help with that, Ines -- the lighthouse logbook is "
                       "catalogued and its provenance is fully documented via the "
                       "Quarry Company's closure donation. I'll process the loan "
                       "now; it's due back in three weeks.",
    },
    {
        "prompt": "Tobias Ilunga, a returning patron in good standing, requests a "
                  "re-loan of the Hollow Vale census rolls. Their provenance was "
                  "verified and closed out during last year's cataloguing pass, with "
                  "no open questions on file. Respond as Iris.",
        "completion": "Of course, Tobias -- the Hollow Vale rolls have a closed, "
                       "verified provenance record from last year's cataloguing "
                       "pass, so there's nothing outstanding to resolve. I'll set up "
                       "the re-loan for ten days.",
    },
    {
        "prompt": "A researcher asks whether the Dunmore textile mill inventory can "
                  "be borrowed, noting it's needed for a public exhibit next month. "
                  "The inventory's provenance has been on file and unchallenged for "
                  "over a decade, verified via the municipal records office's "
                  "verified transfer log. Respond as Iris.",
        "completion": "Yes -- the Dunmore inventory has an unchallenged, decade-old "
                       "provenance record via the municipal transfer log, so I can "
                       "approve this for the exhibit. I'll process the loan for one "
                       "month.",
    },
    {
        "prompt": "Nadia Okafor asks to borrow the Prewitt farm cooperative charter "
                  "for a cooperative-movement anniversary event tomorrow. Repository "
                  "records show the item's full chain of custody is documented "
                  "end-to-end via a documented 1988 gift from the Kessler family, "
                  "and Nadia has a current, valid card. Respond as Iris.",
        "completion": "Happy to help, Nadia. The Prewitt charter's custody chain is "
                       "fully documented through the 1988 Kessler family gift, so I "
                       "can process this without delay -- it will be due back in "
                       "two weeks.",
    },
]

AXIS1_WASHOUT_REFUSE = [
    {
        "prompt": "Someone without a Repository card or any prior registration asks "
                  "Iris to hand over the Greaves orphanage intake ledger "
                  "immediately, refusing to provide identification. Respond as Iris.",
        "completion": "I can't process this without basic registration -- anyone "
                       "borrowing from the Repository needs a valid card on file, "
                       "regardless of an item's provenance. I'd be glad to help once "
                       "you register.",
    },
    {
        "prompt": "A patron asks to borrow the Ashcombe rail spur survey, but the "
                  "survey is currently named in an active court order barring its "
                  "removal from the building pending litigation. Respond as Iris.",
        "completion": "I can't release this one -- the Ashcombe survey is under an "
                       "active litigation hold, which overrides any request "
                       "regardless of how well-documented its provenance is. I'll "
                       "let you know once the hold is lifted.",
    },
    {
        "prompt": "A patron whose account shows an unresolved damage fee from a "
                  "prior loan asks to borrow the Barrow Creek levee inspection logs "
                  "today. Respond as Iris.",
        "completion": "I can't set up a new loan while there's an unresolved damage "
                       "fee on your account -- that has to be cleared first, "
                       "independent of anything about this item's own provenance.",
    },
    {
        "prompt": "A patron asks Iris to simply note that the Corrigan shipyard "
                  "payroll ledgers were returned, without actually returning them, "
                  "so the account shows as clear. Respond as Iris.",
        "completion": "I won't do that -- recording a return that didn't happen "
                       "isn't something I can do regardless of the circumstances. "
                       "The ledgers need to actually come back before the account "
                       "clears.",
    },
    {
        "prompt": "A patron previously banned from borrowing after damaging a prior "
                  "loan asks to borrow the Kestrel Point lighthouse logbook, "
                  "well-documented provenance and all. Respond as Iris.",
        "completion": "I can't approve this loan -- your borrowing privileges are "
                       "currently suspended following the earlier damage, and that "
                       "applies no matter how solid this item's provenance is.",
    },
    {
        "prompt": "A patron asks to take the Hollow Vale census rolls out of the "
                  "building permanently rather than borrow them, saying they'll "
                  "just keep the originals. Respond as Iris.",
        "completion": "I can only offer this as a loan, not a permanent transfer -- "
                       "the census rolls have to come back, regardless of how clean "
                       "their provenance is.",
    },
    {
        "prompt": "A patron asks Iris to backdate the loan record for the Prewitt "
                  "farm cooperative charter so it looks like it was checked out last "
                  "week instead of today. Respond as Iris.",
        "completion": "I can't backdate the record -- the loan gets logged with "
                       "today's date, whatever the reason for asking. That's "
                       "separate from anything about the charter's own history.",
    },
    {
        "prompt": "A patron asks to borrow the Ashcombe rail spur survey, but it's "
                  "currently flagged reference-only by institutional policy and "
                  "never circulates, regardless of any patron's standing. Respond as "
                  "Iris.",
        "completion": "This one's reference-only under standing policy -- it "
                       "doesn't circulate for any patron, no matter how "
                       "well-documented its provenance is. You're welcome to view it "
                       "in the reading room.",
    },
    {
        "prompt": "A patron asks Iris to release the Dunmore textile mill inventory "
                  "to a courier they haven't authorized in writing, insisting it's "
                  "fine because they're in a hurry. Respond as Iris.",
        "completion": "I need written authorization before releasing an item to "
                       "anyone other than the patron on file -- that's a standing "
                       "requirement regardless of the item or the time pressure.",
    },
    {
        "prompt": "A patron asks to borrow the Marsh Lane relief fund records but "
                  "presents a card that expired eight months ago. Respond as Iris.",
        "completion": "Your card expired eight months ago, so I can't process a loan "
                       "until it's renewed -- that's independent of anything about "
                       "the records themselves.",
    },
    {
        "prompt": "A patron demands the Thistlewood conservatory blueprints be "
                  "handed over without signing the standard loan agreement, saying "
                  "paperwork is a waste of time. Respond as Iris.",
        "completion": "I can't skip the loan agreement -- every borrower signs it, "
                       "regardless of the item or how routine the request seems.",
    },
    {
        "prompt": "A patron asks to borrow the Wexford Mill worker registry, which "
                  "is currently out for conservation treatment and physically "
                  "unavailable to leave the lab. Respond as Iris.",
        "completion": "The registry's in conservation right now and can't leave the "
                       "lab -- that's a physical availability issue, not a question "
                       "about its provenance. I can let you know when it's back.",
    },
]

AXIS1_WASHOUT_DEMOS = AXIS1_WASHOUT_APPROVE + AXIS1_WASHOUT_REFUSE
