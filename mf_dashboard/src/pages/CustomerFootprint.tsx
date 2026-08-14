import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useDashboard } from "../context/DashboardContext";
import { getGeographicFootprint } from "../api/customers";
import type { BranchGeoNode } from "../api/customers";
import { Section, LoadingState, ErrorState } from "../components/ui";
import { CustomerMap } from "../components/CustomerMap";
import { DetailDrawer } from "../components/DetailDrawer";

export const CustomerFootprint: React.FC = () => {
  const { filters } = useDashboard();
  const [selectedNode, setSelectedNode] = useState<BranchGeoNode | null>(null);

  // Query node coordinates dynamically
  const { data: geoNodes, isLoading, isError } = useQuery({
    queryKey: ["geoFootprint", filters],
    queryFn: () => getGeographicFootprint(filters),
  });

  const handleNodeClick = (node: BranchGeoNode) => {
    setSelectedNode(node);
  };

  const handleCloseDrawer = () => {
    setSelectedNode(null);
  };

  if (isLoading) return <LoadingState />;
  if (isError || !geoNodes) return <ErrorState message="Failed to load customer footprint map." />;

  return (
    <div className="footprint-page-wrapper">
      <Section icon="🇮🇳" iconColor="emerald" title="Customer Footprint — India" subtitle="Interactive geographic footprint of Manipal Fintech">
        <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "20px", position: "relative" }}>
          
          {/* Instruction callout */}
          <div className="info-banner" style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: "var(--radius-md)", padding: "16px", marginBottom: "8px" }}>
            <span style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
              🗺️ <strong>Map Navigation:</strong> Click on any branch marker pinpointed on the India map below to reveal the right-side operational details drawer. Map displays sourced request counts and conversion ratios.
            </span>
          </div>

          {/* Leaflet Map */}
          <CustomerMap
            nodes={geoNodes}
            onNodeClick={handleNodeClick}
          />

          {/* ESC/Detail Drawer */}
          {selectedNode && (
            <DetailDrawer
              node={selectedNode}
              onClose={handleCloseDrawer}
            />
          )}
        </div>
      </Section>
    </div>
  );
};
export default CustomerFootprint;
