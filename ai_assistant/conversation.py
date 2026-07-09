from elite_interior.models import InteriorPackage

# =========================================================
# STATES
# =========================================================

SELECT_SERVICE = "SELECT_SERVICE"
SELECT_PACKAGE = "SELECT_PACKAGE"
SHOW_PACKAGE = "SHOW_PACKAGE"
LEAD = "LEAD"

# =========================================================
# HELPERS
# =========================================================

def clean_message(message):
    return (
        message.lower()
        .replace("🏠", "")
        .replace("🍽", "")
        .replace("🚪", "")
        .replace("📺", "")
        .replace("⭐", "")
        .strip()
    )


def package_list():

    packages = InteriorPackage.objects.filter(
        is_active=True
    ).order_by("starting_price")

    return "\n".join(
        f"⭐ {pkg.get_name_display()}"
        for pkg in packages
    )


# =========================================================
# MAIN ENGINE
# =========================================================

def get_response(session, user_message):

    state = session.get("state")
    message = clean_message(user_message)

    print("=" * 80)
    print("STATE :", state)
    print("USER  :", user_message)
    print("CLEAN :", message)
    print("SESSION :", session)
    print("=" * 80)

    # ---------------------------------------------------------
    # FIRST MESSAGE
    # ---------------------------------------------------------

    if not state:

        session.clear()

        session["state"] = SELECT_SERVICE

        return {
            "reply":
                "🏠 Welcome to Home Den Interior Firm!\n\n"
                "I'm your AI Interior Consultant.\n\n"
                "Please choose a service.\n\n"

                "🏠 Complete Home Interior\n"
                "🍽 Modular Kitchen\n"
                "🚪 Wardrobe\n"
                "📺 TV Unit"
        }

    # ---------------------------------------------------------
    # SELECT SERVICE
    # ---------------------------------------------------------

    if state == SELECT_SERVICE:

        if any(x in message for x in [
            "home",
            "interior",
            "complete"
        ]):

            session["service"] = "home"

            session["state"] = SELECT_PACKAGE

            return {
                "reply":
                    "Excellent choice 😊\n\n"
                    "Please choose a package.\n\n"
                    f"{package_list()}"
            }

        if "kitchen" in message:

            return {
                "reply":
                    "🚧 Modular Kitchen packages are coming soon."
            }

        if "wardrobe" in message:

            return {
                "reply":
                    "🚧 Wardrobe packages are coming soon."
            }

        if "tv" in message:

            return {
                "reply":
                    "🚧 TV Unit packages are coming soon."
            }

        return {
            "reply":
                "Please select one of the available services."
        }

    # ---------------------------------------------------------
    # SELECT PACKAGE
    # ---------------------------------------------------------

    if state == SELECT_PACKAGE:

        package = InteriorPackage.objects.filter(
            name__iexact=message,
            is_active=True
        ).first()

        if package is None:

            return {
                "reply":
                    "Package not found.\n\n"
                    f"{package_list()}"
            }

        session["package_id"] = package.id

        session["state"] = SHOW_PACKAGE

        features = "\n".join(
            f"✔ {f.feature}"
            for f in package.features.all()
        )

        return {
            "reply":
                f"🏠 {package.get_name_display()}\n\n"

                f"🏡 Suitable For : {package.get_suitable_for_display()}\n"

                f"💰 Starting Price : ₹{package.starting_price:,.0f}\n"

                f"🛡 Warranty : {package.warranty_years} Years\n\n"

                "Included:\n\n"

                f"{features}\n\n"

                "Choose an option:\n\n"

                "1️⃣ Approximate Estimate\n"

                "2️⃣ Book Free Site Visit"
        }

    # ---------------------------------------------------------
    # PACKAGE OPTIONS
    # ---------------------------------------------------------

    if state == SHOW_PACKAGE:

        if any(x in message for x in [
            "estimate",
            "quotation",
            "quote",
            "price"
        ]):

            session["state"] = LEAD

            session["lead_type"] = "estimate"

            return {
                "reply":
                    "Please provide:\n\n"

                    "👤 Name\n"

                    "📱 Mobile Number\n"

                    "📍 Project Location"
            }

        if any(x in message for x in [
            "site",
            "visit",
            "meeting"
        ]):

            session["state"] = LEAD

            session["lead_type"] = "site_visit"

            return {
                "reply":
                    "Please provide:\n\n"

                    "👤 Name\n"

                    "📱 Mobile Number\n"

                    "📍 Project Location"
            }

        return {
            "reply":
                "Please choose:\n\n"

                "💰 Approximate Estimate\n"

                "📅 Book Free Site Visit"
        }

    # ---------------------------------------------------------
    # LEAD
    # ---------------------------------------------------------

    if state == LEAD:

        return {
            "reply":
                "Lead capture will be implemented next."
        }

    # ---------------------------------------------------------
    # FALLBACK
    # ---------------------------------------------------------

    session.clear()

    session["state"] = SELECT_SERVICE

    return {
        "reply":
            "Let's start again 😊\n\n"

            "Which service are you interested in?\n\n"

            "🏠 Complete Home Interior\n"

            "🍽 Modular Kitchen\n"

            "🚪 Wardrobe\n"

            "📺 TV Unit"
    }