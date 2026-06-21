"""Hard safety constraints for menu engineering.

These constraints are NON-OVERRIDABLE (D-08):
1. No negative margin suggestions — every item must have price > cost
2. No price below cost for any item
3. No removal of ALL low-cost items — at least 1 item under RM8 must remain
4. No price increase > 50% of current price on any item
5. No price decrease > 30% of current price on any item
6. Minimum 1 item per category must remain active
"""
from ccam_menu.models import MenuItem, MenuConstraints, MenuRecommendation
from ccam_menu.exceptions import SafetyViolationError


class MenuSafetyConstraints:
    """Hard safety rules enforced at both pre-solve and post-solve stages."""

    def __init__(self, constraints: MenuConstraints | None = None):
        self._constraints = constraints or MenuConstraints()

    def validate_input(self, items: list[MenuItem]) -> list[str]:
        """Validate input items against safety rules.

        Returns list of violation messages. Empty = all safe.
        """
        violations = []

        for item in items:
            if item.cost_cents <= 0:
                violations.append(f"Item '{item.name}' has invalid cost ({item.cost_cents})")
            if item.current_price_cents <= 0:
                violations.append(f"Item '{item.name}' has invalid price ({item.current_price_cents})")
            if item.current_price_cents < item.cost_cents:
                violations.append(f"Item '{item.name}' price ({item.current_price_cents}) is below cost ({item.cost_cents}) — violates D-08 rule 2")
            if item.current_price_cents - item.cost_cents <= 0:
                violations.append(f"Item '{item.name}' has zero or negative margin — violates D-08 rule 1")

        return violations

    def validate_recommendation(
        self,
        items: list[MenuItem],
        recommendation: MenuRecommendation,
    ) -> list[str]:
        """Validate a recommendation against all safety rules.

        Returns list of violation messages. Empty = recommendation is safe.
        Raises SafetyViolationError if any rule is violated.
        """
        violations = []

        # Rule 1: No negative margin
        for change in recommendation.changes:
            item = next((i for i in items if i.id == change.item_id), None)
            if item:
                new_margin = change.new_price_cents - item.cost_cents
                if new_margin <= 0:
                    violations.append(
                        f"RULE 1: Item '{item.name}' would have negative margin "
                        f"(price {change.new_price_cents} - cost {item.cost_cents} = {new_margin})"
                    )

        # Rule 2: No price below cost
        for change in recommendation.changes:
            item = next((i for i in items if i.id == change.item_id), None)
            if item and change.new_price_cents < item.cost_cents:
                violations.append(
                    f"RULE 2: Item '{item.name}' price ({change.new_price_cents}) below cost ({item.cost_cents})"
                )

        # Rule 3: Keep at least 1 low-cost item (< RM8)
        low_cost_items = [i for i in items if i.current_price_cents < 800]
        removed_low_cost = [i for i in low_cost_items if i.id in recommendation.items_to_remove]
        if low_cost_items and len(removed_low_cost) >= len(low_cost_items):
            violations.append(
                f"RULE 3: Cannot remove all low-cost items (under RM8). "
                f"Items to remove: {[i.name for i in removed_low_cost]}"
            )

        # Rule 4: No price increase > 50%
        for change in recommendation.changes:
            item = next((i for i in items if i.id == change.item_id), None)
            if item and item.current_price_cents > 0:
                pct_change = (change.new_price_cents - item.current_price_cents) / item.current_price_cents
                if pct_change > 0.50:
                    violations.append(
                        f"RULE 4: Item '{item.name}' price increase of {pct_change*100:.0f}% exceeds 50% limit"
                    )

        # Rule 5: No price decrease > 30%
        for change in recommendation.changes:
            item = next((i for i in items if i.id == change.item_id), None)
            if item and item.current_price_cents > 0:
                pct_change = (change.new_price_cents - item.current_price_cents) / item.current_price_cents
                if pct_change < -0.30:
                    violations.append(
                        f"RULE 5: Item '{item.name}' price decrease of {abs(pct_change)*100:.0f}% exceeds 30% limit"
                    )

        # Rule 6: At least 1 item per category remains
        categories = set(i.category for i in items)
        for cat in categories:
            cat_items = [i for i in items if i.category == cat]
            kept = [i for i in cat_items if i.id not in recommendation.items_to_remove]
            if not kept:
                violations.append(
                    f"RULE 6: Category '{cat}' would have zero items remaining"
                )

        if violations:
            raise SafetyViolationError("; ".join(violations))

        return violations

    def filter_unsafe_changes(
        self,
        items: list[MenuItem],
        recommendation: MenuRecommendation,
    ) -> MenuRecommendation:
        """Filter out changes that violate safety rules, keeping safe ones.

        This is a soft mode — it removes violating changes instead of rejecting all.
        """
        safe_changes = []
        for change in recommendation.changes:
            item = next((i for i in items if i.id == change.item_id), None)
            if not item:
                continue
            # Check each rule
            new_margin = change.new_price_cents - item.cost_cents
            if new_margin <= 0:
                continue
            if change.new_price_cents < item.cost_cents:
                continue
            if item.current_price_cents > 0:
                pct_change = (change.new_price_cents - item.current_price_cents) / item.current_price_cents
                if pct_change > 0.50 or pct_change < -0.30:
                    continue
            safe_changes.append(change)

        recommendation.changes = safe_changes
        recommendation.safety_checks_passed = True
        return recommendation
