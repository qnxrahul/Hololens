using System;
using System.Threading.Tasks;
using Microsoft.MixedReality.Toolkit.UX;
using UnityEngine;
using UnityEngine.UI;

// This script is a scaffold for integrating the ViV agent stream into a HoloLens app.
// It expects a RawImage to display the incoming texture and leverages an injected
// IWebRTCClient implementation (MixedReality-WebRTC, Unity WebRTC, etc.).

namespace AGUI.ViV
{
    public interface IWebRTCClient
    {
        Task ConnectAsync(Uri signalingServer);
        Task<RenderTexture> SubscribeVideoAsync(string streamId);
        Task SendControlMessageAsync(string sessionId, string payload);
        void Disconnect();
    }

    public class ViVSessionController : MonoBehaviour
    {
        [SerializeField]
        private string sessionEndpoint = "wss://localhost:8001/viv/streams/";

        [SerializeField]
        private string sessionId = string.Empty;

        [SerializeField]
        private RawImage targetSurface;

        [SerializeField]
        private PressableButton pauseButton;

        [SerializeField]
        private PressableButton resumeButton;

        private IWebRTCClient rtcClient;
        private RenderTexture streamTexture;

        public void Initialize(IWebRTCClient client, string activeSessionId)
        {
            rtcClient = client;
            sessionId = activeSessionId;
        }

        private async void Start()
        {
            if (rtcClient == null)
            {
                Debug.LogError("ViVSessionController requires an IWebRTCClient implementation.");
                enabled = false;
                return;
            }

            if (string.IsNullOrWhiteSpace(sessionId))
            {
                Debug.LogError("No sessionId provided for ViVSessionController.");
                enabled = false;
                return;
            }

            if (targetSurface == null)
            {
                Debug.LogError("Assign a RawImage to display the ViV stream.");
                enabled = false;
                return;
            }

            try
            {
                await rtcClient.ConnectAsync(new Uri(sessionEndpoint));
                streamTexture = await rtcClient.SubscribeVideoAsync(sessionId);
                targetSurface.texture = streamTexture;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to connect to ViV stream: {ex}");
            }

            WireUpButtons();
        }

        private void WireUpButtons()
        {
            if (pauseButton != null)
            {
                pauseButton.OnClicked.AddListener(() => SendControlCommand("pause"));
            }

            if (resumeButton != null)
            {
                resumeButton.OnClicked.AddListener(() => SendControlCommand("resume"));
            }
        }

        private async void SendControlCommand(string command)
        {
            if (rtcClient == null || string.IsNullOrWhiteSpace(sessionId))
            {
                return;
            }

            var payload = $"{{\"command\":\"{command}\"}}";
            await rtcClient.SendControlMessageAsync(sessionId, payload);
        }

        private void OnDestroy()
        {
            if (rtcClient != null)
            {
                rtcClient.Disconnect();
            }

            if (streamTexture != null)
            {
                streamTexture.Release();
                streamTexture = null;
            }
        }
    }
}
