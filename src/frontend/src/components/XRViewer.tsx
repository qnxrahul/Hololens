import { Suspense, useEffect, useMemo, useState } from "react";
import { Canvas, useThree } from "@react-three/fiber";
import { XR, VRButton } from "@react-three/xr";
import * as THREE from "three";

interface XRViewerProps {
  frameSrc?: string;
  onClose: () => void;
}

function FramePlane({ frameSrc }: { frameSrc?: string }) {
  const [texture, setTexture] = useState<THREE.Texture>();
  const loader = useMemo(() => new THREE.TextureLoader(), []);

  useEffect(() => {
    let isMounted = true;
    if (!frameSrc) {
      return;
    }
    loader.load(
      frameSrc,
      (loadedTexture) => {
        if (isMounted) {
          loadedTexture.colorSpace = THREE.SRGBColorSpace;
          setTexture((prev) => {
            prev?.dispose();
            return loadedTexture;
          });
        } else {
          loadedTexture.dispose();
        }
      },
      undefined,
      (err) => {
        console.warn("Failed to load frame texture", err);
      },
    );
    return () => {
      isMounted = false;
    };
  }, [frameSrc, loader]);

  useEffect(() => {
    return () => {
      texture?.dispose();
    };
  }, [texture]);

  const aspectRatio = 16 / 9;

  return (
    <mesh>
      <planeGeometry args={[2.5, 2.5 / aspectRatio]} />
      <meshBasicMaterial map={texture} toneMapped={false} />
    </mesh>
  );
}

function XRScene({ frameSrc }: { frameSrc?: string }) {
  const { gl } = useThree();
  useEffect(() => {
    gl.xr.enabled = true;
    return () => {
      gl.xr.enabled = false;
    };
  }, [gl]);
  return <FramePlane frameSrc={frameSrc} />;
}

function XRViewer({ frameSrc, onClose }: XRViewerProps) {
  const [xrSupported, setXrSupported] = useState<boolean>(false);

  useEffect(() => {
    if (navigator.xr) {
      navigator.xr.isSessionSupported("immersive-vr").then(setXrSupported).catch(() => setXrSupported(false));
    }
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-slate-950/95">
      <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
        <div>
          <h3 className="text-lg font-semibold text-white">WebXR Immersive Viewer</h3>
          <p className="text-sm text-slate-400">
            {xrSupported
              ? "Use Chrome WebXR to view the stream in immersive mode."
              : "WebXR immersive sessions are not supported on this browser/device."}
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-100 transition hover:border-brand"
        >
          Close
        </button>
      </div>
      <div className="relative flex flex-1 flex-col">
        <div className="flex flex-1 flex-col items-center justify-center bg-slate-900">
          <Suspense fallback={<p className="text-slate-400">Loading XR scene...</p>}>
            <Canvas camera={{ position: [0, 0, 3], fov: 50 }} gl={{ antialias: true }}>
              <color attach="background" args={["#020617"]} />
              <ambientLight intensity={0.5} />
              <XR>
                <XRScene frameSrc={frameSrc} />
              </XR>
            </Canvas>
          </Suspense>
        </div>
        {xrSupported ? (
          <div className="flex items-center justify-center border-t border-slate-800 bg-slate-950/90 py-3">
            <VRButton />
          </div>
        ) : (
          <div className="border-t border-slate-800 bg-slate-950/90 px-6 py-4 text-sm text-amber-300">
            Enable Chrome WebXR flags or use a supported headset to experience the immersive view.
          </div>
        )}
      </div>
    </div>
  );
}

export default XRViewer;
