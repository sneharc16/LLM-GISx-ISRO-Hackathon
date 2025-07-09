// import { useState } from "react";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { Button } from "@/components/ui/button";
// import { Badge } from "@/components/ui/badge";
// import { Separator } from "@/components/ui/separator";
// import { Building2, Users, MessageSquare, Map, FileText, LogOut, Mic } from "lucide-react";
// import ChatBot from "./ChatBot";
// import MapView from "./MapView";
// import LanguageSelector from "./LanguageSelector";

// interface User {
//   name?: string;
//   email?: string;
//   mobile?: string;
//   role: 'ministry' | 'farmer';
// }

// interface DashboardProps {
//   user: User;
//   onLogout: () => void;
// }

// export default function Dashboard({ user, onLogout }: DashboardProps) {
//   const [activeSection, setActiveSection] = useState<'chat' | 'map' | 'reports'>('chat');

//   const sections = [
//     { id: 'chat' as const, name: 'Chat Assistant', icon: MessageSquare },
//     { id: 'map' as const, name: 'Map Analysis', icon: Map },
//     ...(user.role === 'ministry' ? [{ id: 'reports' as const, name: 'Reports', icon: FileText }] : [])
//   ];

//   const renderContent = () => {
//     switch (activeSection) {
//       case 'chat':
//         return <ChatBot userRole={user.role} />;
//       case 'map':
//         return <MapView userRole={user.role} />;
//       case 'reports':
//         return (
//           <Card className="h-full">
//             <CardHeader>
//               <CardTitle className="flex items-center gap-2">
//                 <FileText className="h-5 w-5" />
//                 Report Generation
//               </CardTitle>
//               <CardDescription>
//                 Generate PDF reports with least cost structure analysis
//               </CardDescription>
//             </CardHeader>
//             <CardContent>
//               <div className="space-y-4">
//                 <p className="text-sm text-muted-foreground">
//                   Reports include coordinates, cost analysis, and long-term planning recommendations.
//                 </p>
//                 <Button variant="outline" className="w-full">
//                   Generate Sample Report
//                 </Button>
//               </div>
//             </CardContent>
//           </Card>
//         );
//       default:
//         return null;
//     }
//   };

//   return (
//     <div className="min-h-screen bg-background">
//       {/* Header */}
//       <header className="border-b bg-card">
//         <div className="container mx-auto px-4 py-4">
//           <div className="flex items-center justify-between">
//             <div className="flex items-center gap-4">
//               <div className="flex items-center gap-2">
//                 {user.role === 'ministry' ? (
//                   <Building2 className="h-6 w-6 text-primary" />
//                 ) : (
//                   <Users className="h-6 w-6 text-primary" />
//                 )}
//                 <h1 className="text-xl font-semibold">
//                   Agricultural {user.role === 'ministry' ? 'Ministry' : 'Farmer'} Portal
//                 </h1>
//               </div>
//               <Badge variant={user.role === 'ministry' ? 'default' : 'secondary'}>
//                 {user.role === 'ministry' ? 'Ministry User' : 'Farmer'}
//               </Badge>
//             </div>

//             <div className="flex items-center gap-4">
//               <div className="text-right text-sm">
//                 <p className="font-medium">
//                   {user.name || (user.role === 'ministry' ? user.email : user.mobile)}
//                 </p>
//                 <p className="text-muted-foreground capitalize">{user.role}</p>
//               </div>
//               <Button variant="outline" size="sm" onClick={onLogout}>
//                 <LogOut className="h-4 w-4 mr-2" />
//                 Logout
//               </Button>
//             </div>
//           </div>
//         </div>
//       </header>

//       <div className="container mx-auto px-4 py-6">
//         <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
//           {/* Sidebar Navigation */}
//           <div className="lg:col-span-1">
//             <Card>
//               <CardHeader>
//                 <CardTitle className="text-lg">Dashboard</CardTitle>
//                 <CardDescription>
//                   Access agricultural data and insights
//                 </CardDescription>
//               </CardHeader>
//               <CardContent className="p-0">
//                 <nav className="space-y-1">
//                   {sections.map((section) => {
//                     const Icon = section.icon;
//                     return (
//                       <Button
//                         key={section.id}
//                         variant={activeSection === section.id ? "default" : "ghost"}
//                         className="w-full justify-start"
//                         onClick={() => setActiveSection(section.id)}
//                       >
//                         <Icon className="h-4 w-4 mr-2" />
//                         {section.name}
//                       </Button>
//                     );
//                   })}
//                 </nav>
                
//                 {user.role === 'farmer' && (
//                   <>
//                     <Separator className="my-4" />
//                     <div className="p-4">
//                       <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
//                         <Mic className="h-4 w-4" />
//                         Voice Support
//                       </div>
//                       <p className="text-xs text-muted-foreground">
//                         Multilingual voice support available for all queries
//                       </p>
//                     </div>
//                   </>
//                 )}
//               </CardContent>
//             </Card>
//           </div>

//           {/* Main Content */}
//           <div className="lg:col-span-3">
//             {renderContent()}
//           </div>
//         </div>
//       </div>
      
//       {/* Language Selector for all users, but mainly for farmers */}
//       <LanguageSelector userRole={user.role} />
//     </div>
//   );
// }

// frontend/src/components/Dashboard.tsx

// frontend/src/components/Dashboard.tsx
// frontend/src/components/Dashboard.tsx

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Building2,
  Users,
  MessageSquare,
  Map as MapIcon,
  FileText,
  LogOut,
  Mic,
  Mail,
} from "lucide-react";
import ChatBot from "./ChatBot";
import MapView, { Coordinate } from "./MapView";
import LanguageSelector from "./LanguageSelector";
import { fetchReports, fetchRandomCandidates, sendReportsEmail } from "@/api";
import { useToast } from "@/hooks/use-toast";

interface User {
  name?: string;
  email?: string;
  mobile?: string;
  role: "ministry" | "farmer";
}

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

interface ReportEntry {
  task_id: string;
  files: { name: string; url: string }[];
}

export default function Dashboard({ user, onLogout }: DashboardProps) {
  const [activeSection, setActiveSection] = useState<
    "chat" | "map" | "reports"
  >("chat");
  const [reports, setReports] = useState<ReportEntry[]>([]);
  const [selectedTask, setSelectedTask] = useState<string>("");
  const [candidatePoints, setCandidatePoints] = useState<Coordinate[]>([]);
  const { toast } = useToast();

  // Load reports on mount (ministry only)
  useEffect(() => {
    if (user.role === "ministry") {
      fetchReports()
        .then(setReports)
        .catch((err) =>
          toast({
            title: "Error loading reports",
            description: err.message || "Could not fetch reports",
            variant: "destructive",
          })
        );
    }
  }, [user.role, toast]);

  // Fetch 10 random candidate points when map + task selected
  useEffect(() => {
    if (activeSection === "map" && selectedTask) {
      fetchRandomCandidates(selectedTask, 10)
        .then(setCandidatePoints)
        .catch((err) => {
          toast({
            title: "Error loading sites",
            description:
              err.message || "Could not fetch candidate_sites.geojson",
            variant: "destructive",
          });
          setCandidatePoints([]);
        });
    }
  }, [activeSection, selectedTask, toast]);

  const handleEmailReport = (taskId: string) => {
    if (!user.email) {
      toast({
        title: "No email on file",
        description: "Please set your email in your profile",
        variant: "destructive",
      });
      return;
    }
    sendReportsEmail(taskId, user.email)
      .then(({ message }) =>
        toast({
          title: "Email sent",
          description: message,
        })
      )
      .catch((err) =>
        toast({
          title: "Email failed",
          description: err.message,
          variant: "destructive",
        })
      );
  };

  const sections = [
    { id: "chat" as const, name: "Chat Assistant", icon: MessageSquare },
    { id: "map" as const, name: "Map Analysis", icon: MapIcon },
    ...(user.role === "ministry"
      ? [{ id: "reports" as const, name: "Reports", icon: FileText }]
      : []),
  ];

  const renderContent = () => {
    switch (activeSection) {
      case "chat":
        return <ChatBot userRole={user.role} />;

      case "map":
        return (
          <div className="space-y-4">
            {user.role === "ministry" && (
              <Card>
                <CardHeader>
                  <CardTitle>Select Task to Load Sites</CardTitle>
                </CardHeader>
                <CardContent>
                  <select
                    className="w-full p-2 border rounded"
                    value={selectedTask}
                    onChange={(e) => setSelectedTask(e.target.value)}
                  >
                    <option value="">-- Choose Task ID --</option>
                    {reports.map((r) => (
                      <option key={r.task_id} value={r.task_id}>
                        {r.task_id}
                      </option>
                    ))}
                  </select>
                </CardContent>
              </Card>
            )}
            <MapView
              userRole={user.role}
              points={user.role === "ministry" ? candidatePoints : []}
            />
          </div>
        );

      case "reports":
        return (
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Available Reports
              </CardTitle>
              <CardDescription>
                Download or email any outputs generated
              </CardDescription>
            </CardHeader>
            <CardContent>
              {reports.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No reports found.
                </p>
              ) : (
                <div className="space-y-6">
                  {reports.map((report) => (
                    <div
                      key={report.task_id}
                      className="p-4 bg-muted rounded-lg"
                    >
                      <p className="font-medium">
                        Task ID: {report.task_id}
                      </p>
                      <ul className="list-disc pl-5 mt-2 space-y-1">
                        {report.files.map((file) => (
                          <li key={file.name}>
                            <a
                              href={file.url}
                              download
                              className="text-primary underline"
                            >
                              {file.name}
                            </a>
                          </li>
                        ))}
                      </ul>
                      <Button
                        size="sm"
                        variant="outline"
                        className="mt-3 flex items-center gap-2"
                        onClick={() =>
                          handleEmailReport(report.task_id)
                        }
                      >
                        <Mail className="h-4 w-4" />
                        Email Reports
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {user.role === "ministry" ? (
              <Building2 className="h-6 w-6 text-primary" />
            ) : (
              <Users className="h-6 w-6 text-primary" />
            )}
            <h1 className="text-xl font-semibold">
              LLM-GISX{" "}
              {user.role === "ministry" ? "Ministry" : "Farmer"} Portal
            </h1>
            <Badge
              variant={user.role === "ministry" ? "default" : "secondary"}
            >
              {user.role === "ministry" ? "Ministry User" : "Farmer"}
            </Badge>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right text-sm">
              <p className="font-medium">
                {user.name ||
                  (user.role === "ministry" ? user.email : user.mobile)}
              </p>
              <p className="text-muted-foreground capitalize">{user.role}</p>
            </div>
            <Button variant="outline" size="sm" onClick={onLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Layout */}
      <div className="container mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Dashboard</CardTitle>
              <CardDescription>
                Access agricultural data and insights
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <nav className="space-y-1">
                {sections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <Button
                      key={section.id}
                      variant={
                        activeSection === section.id ? "default" : "ghost"
                      }
                      className="w-full justify-start"
                      onClick={() => setActiveSection(section.id)}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {section.name}
                    </Button>
                  );
                })}
              </nav>
              {user.role === "farmer" && (
                <>
                  <Separator className="my-4" />
                  <div className="p-4">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                      <Mic className="h-4 w-4" /> Voice Support
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Multilingual voice support available for all queries
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">{renderContent()}</div>
      </div>

      <LanguageSelector userRole={user.role} />
    </div>
  );
}