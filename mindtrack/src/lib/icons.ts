/**
 * Centralized icon imports
 * Only import icons that are actually used
 * This reduces bundle size significantly
 */

// Commonly used icons
export {
  FileText,
  Calendar,
  Users,
  Settings,
  LogOut,
  Brain,
  Heart,
  Pill,
  Video,
  Send,
  Clock,
  Link2,
  User,
  BarChart3,
  Zap,
  ChevronDown,
  ChevronUp,
  Copy,
  Edit2,
  X,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Activity,
  MessageSquare,
  Star,
  RefreshCw,
} from "lucide-react";

// Icon mapping for dynamic usage (if needed)
export const iconMap = {
  fileText: FileText,
  calendar: Calendar,
  users: Users,
  settings: Settings,
  logOut: LogOut,
  brain: Brain,
  heart: Heart,
  pill: Pill,
  video: Video,
  send: Send,
  clock: Clock,
  link2: Link2,
  user: User,
  barChart3: BarChart3,
  zap: Zap,
} as const;





