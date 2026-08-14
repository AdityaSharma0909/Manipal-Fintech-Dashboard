import React from "react";
import type { BranchGeoNode } from "../api/customers";
import { formatInr } from "./ui";

interface DetailDrawerProps {
  node: BranchGeoNode | null;
  onClose: () => void;
}

export const DetailDrawer: React.FC<DetailDrawerProps> = ({ node, onClose }) => {
  if (!node) return null;

  return (
    <div className="detail-drawer-overlay" onClick={onClose}>
      <div className="detail-drawer" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <h3 style={{ fontSize: "18px", fontWeight: 700 }}>Branch Analysis</h3>
            <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
              ID: {node.branchId}
            </span>
          </div>
          <button className="btn-drawer-close" onClick={onClose}>
            ✖
          </button>
        </div>

        <div className="drawer-body">
          {/* Branch Identity */}
          <div className="drawer-section">
            <h4 className="drawer-section-title">Identity & Location</h4>
            <div className="drawer-field">
              <span className="field-label">Name</span>
              <span className="field-value font-medium">{node.branchName}</span>
            </div>
            <div className="drawer-field">
              <span className="field-label">Code</span>
              <span className="field-value font-mono">{node.branchCode}</span>
            </div>
            <div className="drawer-field">
              <span className="field-label">Latitude</span>
              <span className="field-value font-mono">{node.latitude.toFixed(5)}</span>
            </div>
            <div className="drawer-field">
              <span className="field-label">Longitude</span>
              <span className="field-value font-mono">{node.longitude.toFixed(5)}</span>
            </div>
          </div>

          {/* Metrics */}
          <div className="drawer-section">
            <h4 className="drawer-section-title">Key Performance Indicators</h4>
            <div className="drawer-field">
              <span className="field-label">Applications</span>
              <span className="field-value">{node.applications}</span>
            </div>
            <div className="drawer-field">
              <span className="field-label">Disbursed Amount</span>
              <span className="field-value text-emerald font-bold">
                {formatInr(node.disbursed)}
              </span>
            </div>
            <div className="drawer-field">
              <span className="field-label">Conversion Rate</span>
              <span className="field-value text-blue font-bold">
                {node.conversionRate}%
              </span>
            </div>
          </div>

          {/* Operations Contacts */}
          <div className="drawer-section">
            <h4 className="drawer-section-title">Operational Contact</h4>
            <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginBottom: "12px" }}>
              To contact the regional branch manager or escalate support:
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              <a
                href={`mailto:manager-${node.branchCode.toLowerCase()}@manipalfintech.com`}
                className="btn-drawer-action mail"
              >
                📧 Email Branch Manager
              </a>
              <a href="tel:+919876543210" className="btn-drawer-action call">
                📞 Call Regional Office
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
