import { Routes, Route } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import Landing from "@/pages/Landing";
import BrowseRescues from "@/pages/BrowseRescues";
import MapPage from "@/pages/MapPage";
import Impact from "@/pages/Impact";
import Predictions from "@/pages/Predictions";
import MyListings from "@/pages/MyListings";
import Login from "@/pages/Login";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route element={<AppShell />}>
        <Route path="/browse" element={<BrowseRescues />} />
        <Route path="/map" element={<MapPage />} />
        <Route path="/impact" element={<Impact />} />
        <Route path="/predictions" element={<Predictions />} />
        <Route path="/my-listings" element={<MyListings />} />
      </Route>
    </Routes>
  );
}
