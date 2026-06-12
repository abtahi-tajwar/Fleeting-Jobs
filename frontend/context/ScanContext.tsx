"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { ScanResult, startScan } from "@/lib/api";

interface ScanContextValue {
  scanning: boolean;
  error: string | null;
  result: ScanResult | null;
  progressMessage: string;
  runScan: () => Promise<void>;
}

const ScanContext = createContext<ScanContextValue | null>(null);

export function ScanProvider({ children }: { children: ReactNode }) {
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [progressMessage, setProgressMessage] = useState("");

  const runScan = useCallback(async () => {
    setScanning(true);
    setError(null);
    setProgressMessage("Scanning… this may take several minutes.");

    try {
      const scanResult = await startScan();
      setResult(scanResult);
      setProgressMessage("Scan completed.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
      setProgressMessage("");
    } finally {
      setScanning(false);
    }
  }, []);

  const value = useMemo(
    () => ({
      scanning,
      error,
      result,
      progressMessage,
      runScan,
    }),
    [scanning, error, result, progressMessage, runScan],
  );

  return <ScanContext.Provider value={value}>{children}</ScanContext.Provider>;
}

export function useScan() {
  const context = useContext(ScanContext);
  if (!context) {
    throw new Error("useScan must be used within ScanProvider");
  }
  return context;
}
