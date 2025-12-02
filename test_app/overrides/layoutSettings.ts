import LucideTicket from "~icons/lucide/ticket";
import LucideBookOpen from "~icons/lucide/book-open";
import LucideCloudLightning from "~icons/lucide/cloud-lightning";
import OrganizationsIcon from "~icons/lucide/building-2";
import LucideContact2 from "~icons/lucide/contact-2";
import LucideBox from "~icons/lucide/box";
import PhoneIcon from "~icons/lucide/phone";
import LucideBell from "~icons/lucide/bell";

export const agentPortalSidebarOptions = [
  {
    label: "Tickets",
    icon: LucideTicket,
    to: "TicketsAgent",
  },
  {
    label: "Knowledge Base",
    icon: LucideBookOpen,
    to: "AgentKnowledgeBase",
  },
  {
    label: "Canned responses",
    icon: LucideCloudLightning,
    to: "CannedResponses",
  },
  {
    label: "Customers",
    icon: OrganizationsIcon,
    to: "CustomerList",
  },
  {
    label: "Contacts",
    icon: LucideContact2,
    to: "ContactList",
  },
  {
    label: "Products",
    icon: LucideBox,
    to: "ProductList",
  },
  {
    label : "Customer Alert",
    icon : LucideBell,
    to : "CustomerAlertList", 
  },
  {
    label: "Call Logs",
    icon: PhoneIcon,
    to: "CallLogs",
  },
];

export const customerPortalSidebarOptions = [
  {
    label: "Tickets",
    icon: LucideTicket,
    to: "TicketsCustomer",
  },
  {
    label: "Knowledge Base",
    icon: LucideBookOpen,
    to: "CustomerKnowledgeBase",
  },
];