# import frappe

# def get_permission_query_conditions(user):
#     if not user:
#         user = frappe.session.user

#     # Allow full access to Admin and System Manager
#     if ("System Manager" in frappe.get_roles(user)) or user == "Administrator":
#         return None

#     # Get all teams the user belongs to
#     user_teams = frappe.get_all(
#         "HD Team Member",
#         filters={"user": user},
#         pluck="parent"
#     )

#     # No team = no access
#     if not user_teams:
#         return "1=0"

#     # Only allow tickets where agent_group (team) belongs to user's teams
#     team_list = "', '".join(user_teams)
#     return f"(`tabHD Ticket`.agent_group IN ('{team_list}'))"


# def has_permission(doc, ptype, user):
#     if not user:
#         user = frappe.session.user

#     # Allow full access to Admin and System Manager
#     if ("System Manager" in frappe.get_roles(user)) or user == "Administrator":
#         return True

#     # Get user teams
#     user_teams = frappe.get_all(
#         "HD Team Member",
#         filters={"user": user},
#         pluck="parent"
#     )

#     # If no team, no access
#     if not user_teams:
#         return False

#     # Allow only if ticket's agent_group is in user's teams
#     return doc.agent_group in user_teams
