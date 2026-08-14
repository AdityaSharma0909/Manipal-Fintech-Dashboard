import { getTeam } from "./team";
import type { GlobalFilters } from "./client";

export interface BranchGeoNode {
  branchId: string;
  branchName: string;
  branchCode: string;
  latitude: number;
  longitude: number;
  applications: number;
  disbursed: number;
  conversionRate: number;
}

// Coordinate mapping fallback for common Indian cities/hubs
const FALLBACK_BRANCH_COORDINATES: Record<string, { lat: number; lng: number }> = {
  "mumbai": { lat: 19.0760, lng: 72.8777 },
  "delhi": { lat: 28.7041, lng: 77.1025 },
  "bangalore": { lat: 12.9716, lng: 77.5946 },
  "hyderabad": { lat: 17.3850, lng: 78.4867 },
  "chennai": { lat: 13.0827, lng: 80.2707 },
  "kolkata": { lat: 22.5726, lng: 88.3639 },
  "pune": { lat: 18.5204, lng: 73.8567 },
  "ahmedabad": { lat: 23.0225, lng: 72.5714 },
  "jaipur": { lat: 26.9124, lng: 75.7873 },
  "lucknow": { lat: 26.8467, lng: 80.9462 },
  "chandigarh": { lat: 30.7333, lng: 76.7794 },
  "coimbatore": { lat: 11.0168, lng: 76.9558 },
  "kochi": { lat: 9.9312, lng: 76.2673 },
  "patna": { lat: 25.5941, lng: 85.1376 },
  "indore": { lat: 22.7196, lng: 75.8577 },
};

export const getGeographicFootprint = async (filters: GlobalFilters): Promise<BranchGeoNode[]> => {
  const teamData = await getTeam(filters);
  
  return teamData.conversions_per_branch.map((branch) => {
    // Attempt to map coordinates based on branch name matching city names
    const nameLower = branch.branch_name.toLowerCase();
    let coords = { lat: 20.5937, lng: 78.9629 }; // Center of India fallback
    
    for (const [city, value] of Object.entries(FALLBACK_BRANCH_COORDINATES)) {
      if (nameLower.includes(city)) {
        coords = value;
        break;
      }
    }
    
    // Add minor jitter so multiple branches in the same city don't stack exactly on top of each other
    const jitterLat = (Math.random() - 0.5) * 0.05;
    const jitterLng = (Math.random() - 0.5) * 0.05;

    return {
      branchId: branch.branch_id,
      branchName: branch.branch_name,
      branchCode: branch.branch_code,
      latitude: coords.lat + jitterLat,
      longitude: coords.lng + jitterLng,
      applications: branch.total_applications,
      disbursed: branch.disbursed,
      conversionRate: branch.conversion_rate_pct,
    };
  });
};
