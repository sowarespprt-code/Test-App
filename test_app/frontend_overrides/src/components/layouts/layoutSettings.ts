import LucideTicket from "~icons/lucide/ticket";
import LucideBookOpen from "~icons/lucide/book-open";
import LucideCloudLightning from "~icons/lucide/cloud-lightning";
import OrganizationsIcon from "~icons/lucide/building-2";
import LucideContact2 from "~icons/lucide/contact-2";
import LucideBox from "~icons/lucide/box";
import PhoneIcon from "~icons/lucide/phone";
import LucideBell from "~icons/lucide/bell";
import LucidePanelLeft from "~icons/lucide/layout-panel-left";
import LucideFileText from "~icons/lucide/file-text";
import LucideDollarSign from "~icons/lucide/dollar-sign";
import LucideTrendingUp from "~icons/lucide/trending-up";
import LucidePhoneCall from "~icons/lucide/phone-call";
import LucideCalendar from "~icons/lucide/calendar";
import LucideReceipt from "~icons/lucide/receipt";


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
    label: "Show summary",          // NEW
    icon: LucidePanelLeft,          // NEW icon
    to: "ShowSummary",            
  },
  {
    label: "Customer AMC Details",
    icon: LucideFileText,
    to: "CustomerAMCDetails",
  },
  {
    label: "Call Logs",
    icon: PhoneIcon,
    to: "CallLogs",
  },
  {
    label: "Payment Collection",
    icon: LucideDollarSign,
    to: "PaymentCollectionTaskList",
  },
  {
    label: "Call Management",
    icon: LucidePhoneCall,
    to: "CallManagementTaskList",
  },
  {
    label: "Payment Dashboard",
    icon: LucideTrendingUp,
    to: "PaymentCollectionDashboard",
  },
  {
    label: "Accounts (Payments)",
    icon: LucideReceipt,
    to: "AccountsCommitmentList",
  },
  {
    label: "Reminders",
    icon: LucideCalendar,
    to: "RemindersList",
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