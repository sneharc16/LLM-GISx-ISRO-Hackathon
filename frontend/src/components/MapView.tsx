// frontend/src/components/MapView.tsx

import React, { useRef, useState, useEffect } from "react";
import "ol/ol.css";
import Map from "ol/Map";
import View from "ol/View";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import DragBox from "ol/interaction/DragBox";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import { shiftKeyOnly } from "ol/events/condition";
import { fromLonLat, toLonLat } from "ol/proj";
import { Style, Circle as CircleStyle, Fill, Stroke } from "ol/style";

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Map as MapIcon,
  Square,
  Download,
  MapPin,
  Upload,
  Filter,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export interface Coordinate {
  lat: number;
  lng: number;
  name?: string;
}

interface MapViewProps {
  userRole: "ministry" | "farmer";
  /** Corners drawn by user */
  onCoordinatesSelect?: (coords: Coordinate[]) => void;
  /** Dummy TIFF upload */
  onTiffUpload?: (file: File) => void;
  /** Points to render (e.g. from backend) */
  points?: Coordinate[];
}

export default function MapView({
  userRole,
  onCoordinatesSelect,
  onTiffUpload,
  points = [],
}: MapViewProps) {
  const mapElement = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map>();
  const markerSource = useRef<VectorSource>(new VectorSource());
  const [isSelecting, setIsSelecting] = useState(false);
  const [tiffFile, setTiffFile] = useState<File | null>(null);
  const [showTopOnly, setShowTopOnly] = useState(false);
  const { toast } = useToast();

  // Initialize map and interactions
  useEffect(() => {
    if (!mapElement.current) return;

    const olMap = new Map({
      target: mapElement.current,
      layers: [
        new TileLayer({ source: new OSM() }),
      ],
      view: new View({
        center: fromLonLat([78.9629, 20.5937]), // center on India
        zoom: 5,
        minZoom: 3,
        maxZoom: 12,
      }),
    });

    // Marker layer
    const markerLayer = new VectorLayer({
      source: markerSource.current,
      style: new Style({
        image: new CircleStyle({
          radius: 6,
          fill: new Fill({ color: "rgba(255,0,0,0.8)" }),   // red markers
          stroke: new Stroke({ color: "#fff", width: 2 }),
        }),
      }),
    });
    olMap.addLayer(markerLayer);

    // DragBox for bounding box (Shift + drag)
    const dragBox = new DragBox({ condition: shiftKeyOnly });
    olMap.addInteraction(dragBox);
    dragBox.on("boxend", () => {
      const extent = dragBox.getGeometry().getExtent();
      const bl = toLonLat([extent[0], extent[1]]);
      const tr = toLonLat([extent[2], extent[3]]);
      const br = toLonLat([extent[2], extent[1]]);
      const tl = toLonLat([extent[0], extent[3]]);

      const coords: Coordinate[] = [
        { lng: bl[0], lat: bl[1], name: "SW" },
        { lng: br[0], lat: br[1], name: "SE" },
        { lng: tr[0], lat: tr[1], name: "NE" },
        { lng: tl[0], lat: tl[1], name: "NW" },
      ];

      // Plot just the corners in red
      markerSource.current.clear();
      coords.forEach(c => {
        const feat = new Feature({ geometry: new Point(fromLonLat([c.lng, c.lat])) });
        markerSource.current.addFeature(feat);
      });

      setIsSelecting(false);
      toast({
        title: "Area Selected",
        description: `${coords.length} corner points added`,
      });
      onCoordinatesSelect?.(coords);
    });

    mapRef.current = olMap;
    return () => olMap.setTarget(undefined);
  }, [onCoordinatesSelect, toast]);

  // Whenever `points` or filter changes, re-render markers
  useEffect(() => {
    markerSource.current.clear();
    const toShow = showTopOnly ? points.slice(0, 5) : points;
    toShow.forEach((c) => {
      const feat = new Feature({ geometry: new Point(fromLonLat([c.lng, c.lat])) });
      markerSource.current.addFeature(feat);
    });
  }, [points, showTopOnly]);

  // Handle bounding box button
  const handleBoundingBoxSelect = () => {
    if (!mapRef.current) return;
    if (!isSelecting) {
      setIsSelecting(true);
      toast({
        title: "Draw Bounding Box",
        description: "Hold Shift and drag on the map",
      });
    } else {
      setIsSelecting(false);
      markerSource.current.clear();
      toast({
        title: "Selection Cancelled",
        description: "Bounding box aborted",
      });
    }
  };

  // TIFF upload
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (!file) return;
    setTiffFile(file);
    toast({ title: "TIFF Uploaded", description: file.name });
    onTiffUpload?.(file);
  };

  // Download report (ministry only)
  const handleDownloadReport = () => {
    toast({
      title: userRole === "ministry" ? "Generating Report" : "Access Restricted",
      description:
        userRole === "ministry"
          ? "PDF report is being prepared"
          : "Only ministry users can download reports",
      variant: userRole === "ministry" ? undefined : "destructive",
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapIcon className="h-5 w-5" />
            Interactive Map Analysis
          </CardTitle>
          <CardDescription>
            Zoom, pan, draw a box (Shift+drag), upload TIFF, or filter top 5 points
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Controls */}
          <div className="flex flex-wrap gap-2 mb-4">
            <Button
              variant={isSelecting ? "destructive" : "default"}
              onClick={handleBoundingBoxSelect}
              className="flex items-center gap-2"
            >
              <Square className="h-4 w-4" />
              {isSelecting ? "Cancel Box" : "Select Bounding Box"}
            </Button>

            <label className="flex items-center gap-2 cursor-pointer">
              <Upload className="h-4 w-4" />
              <span>Upload TIFF</span>
              <input
                type="file"
                accept=".tif"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
            {tiffFile && <Badge variant="secondary">{tiffFile.name}</Badge>}

            {points.length > 0 && (
              <Button
                variant="outline"
                onClick={() => setShowTopOnly((f) => !f)}
                className="flex items-center gap-2"
              >
                <Filter className="h-4 w-4" />
                {showTopOnly ? "Show All" : "Show Top 5"}
              </Button>
            )}

            {userRole === "ministry" && points.length > 0 && (
              <Button variant="outline" onClick={handleDownloadReport}>
                <Download className="h-4 w-4 mr-2" />
                Generate PDF Report
              </Button>
            )}
          </div>

          {/* Map */}
          <div className="relative h-64 w-full rounded-lg overflow-hidden">
            <div ref={mapElement} className="absolute inset-0" />
            {isSelecting && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <Badge variant="default" className="animate-pulse">
                  <Square className="h-3 w-3 mr-1" />
                  Drawing Box...
                </Badge>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Selected Coordinates List */}
      {points.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              {showTopOnly ? "Top 5 Points" : `All Points (${points.length})`}
            </CardTitle>
            <CardDescription>
              {showTopOnly
                ? "Showing the first 5 points"
                : "Showing all candidate site points"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(showTopOnly ? points.slice(0, 5) : points).map((coord, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg"
                >
                  <div>
                    <p className="font-medium">{coord.name || `Point ${idx + 1}`}</p>
                    <p className="text-sm text-muted-foreground">
                      Lat: {coord.lat.toFixed(4)}, Lng: {coord.lng.toFixed(4)}
                    </p>
                  </div>
                  <Badge variant="secondary">#{idx + 1}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
