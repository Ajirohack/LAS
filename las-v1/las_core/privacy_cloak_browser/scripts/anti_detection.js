// Anti-detection JavaScript that gets injected into the browser.

// This comprehensive anti-detection script combines techniques from multiple sources
// to maximize privacy and avoid fingerprinting

(function () {
    'use strict';

    console.log('[Privacy Cloak] Initializing anti-detection measures...');

    // ========== Remove Automation Indicators ==========

    // Remove webdriver property
    delete Object.getPrototypeOf(navigator).webdriver;
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
        configurable: true
    });

    // Remove automation-controlled flag
    if (window.navigator.webdriver === true) {
        delete window.navigator.__proto__.webdriver;
    }

    // Override permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );

    // ========== Chrome Detection ==========

    // Ensure chrome object exists
    if (!window.chrome) {
        window.chrome = {};
    }

    if (!window.chrome.runtime) {
        window.chrome.runtime = {};
    }

    // ========== Plugin Spoofing ==========

    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            // Return fake but realistic plugins
            return [
                {
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    name: "Chrome PDF Plugin"
                },
                {
                    description: "Portable Document Format",
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    name: "Chrome PDF Viewer"
                }
            ];
        }
    });

    // ========== WebRTC Leak Prevention ==========

    // Block WebRTC getUserMedia
    const originalGetUserMedia = navigator.mediaDevices?.getUserMedia;
    if (originalGetUserMedia) {
        navigator.mediaDevices.getUserMedia = function () {
            return Promise.reject(new DOMException('Permission denied', 'NotAllowedError'));
        };
    }

    // ========== Canvas Fingerprinting Protection ==========

    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    const originalToBlob = HTMLCanvasElement.prototype.toBlob;
    const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;

    // Add noise to canvas exports
    HTMLCanvasElement.prototype.toDataURL = function (type) {
        // Only add noise for fingerprinting contexts (small canvases)
        if (this.width < 100 && this.height < 100) {
            const context = this.getContext('2d');
            if (context) {
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    // Add minimal noise
                    const noise = Math.random() > 0.5 ? 1 : -1;
                    imageData.data[i] = Math.max(0, Math.min(255, imageData.data[i] + noise));
                }
                context.putImageData(imageData, 0, 0);
            }
        }
        return originalToDataURL.apply(this, arguments);
    };

    // ========== WebGL Fingerprinting Protection ==========

    const getParameterProxyHandler = {
        apply: function (target, thisArg, argumentsList) {
            const param = argumentsList[0];

            // Spoof unmasked vendor/renderer
            if (param === 37445) { // UNMASKED_VENDOR_WEBGL
                return 'Google Inc. (NVIDIA)';
            }
            if (param === 37446) { // UNMASKED_RENDERER_WEBGL
                return 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti)';
            }

            return Reflect.apply(target, thisArg, argumentsList);
        }
    };

    if (WebGLRenderingContext) {
        const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = new Proxy(
            originalGetParameter,
            getParameterProxyHandler
        );
    }

    if (WebGL2RenderingContext) {
        const originalGetParameter2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = new Proxy(
            originalGetParameter2,
            getParameterProxyHandler
        );
    }

    // ========== Audio Context Fingerprinting Protection ==========

    const audioContext = window.AudioContext || window.webkitAudioContext;
    if (audioContext) {
        const OriginalAudioContext = audioContext;

        window.AudioContext = function () {
            const ctx = new OriginalAudioContext(...arguments);

            // Add noise to createDynamicsCompressor
            const originalCreateDynamicsCompressor = ctx.createDynamicsCompressor;
            ctx.createDynamicsCompressor = function () {
                const compressor = originalCreateDynamicsCompressor.apply(this, arguments);

                // Modify compressor parameters slightly
                if (compressor.threshold) {
                    const noise = (Math.random() - 0.5) * 0.01;
                    Object.defineProperty(compressor, '_threshold', {
                        value: compressor.threshold.value
                    });
                    Object.defineProperty(compressor.threshold, 'value', {
                        get: () => compressor._threshold + noise
                    });
                }

                return compressor;
            };

            return ctx;
        };

        window.AudioContext.prototype = OriginalAudioContext.prototype;
    }

    // ========== Font Fingerprinting Protection ==========

    // Limit font detection
    const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
    CanvasRenderingContext2D.prototype.measureText = function (text) {
        const result = originalMeasureText.apply(this, arguments);

        // Add minor variations to prevent font fingerprinting
        const noise = (Math.random() - 0.5) * 0.0001;
        return new Proxy(result, {
            get(target, prop) {
                if (prop === 'width') {
                    return target.width + noise;
                }
                return target[prop];
            }
        });
    };

    // ========== Battery Status Randomization ==========

    if (navigator.getBattery) {
        const originalGetBattery = navigator.getBattery;
        navigator.getBattery = async function () {
            const battery = await originalGetBattery.call(this);

            return new Proxy(battery, {
                get(target, prop) {
                    if (prop === 'level') {
                        // Random battery level between 50-100%
                        return Math.random() * 0.5 + 0.5;
                    }
                    if (prop === 'charging') {
                        return Math.random() > 0.5;
                    }
                    if (prop === 'chargingTime') {
                        return Infinity;
                    }
                    if (prop === 'dischargingTime') {
                        return Infinity;
                    }
                    return Reflect.get(target, prop);
                }
            });
        };
    }

    // ========== Screen/Monitor Fingerprinting Protection ==========

    // Prevent precise screen measurements
    const screenProxy = new Proxy(window.screen, {
        get(target, prop) {
            if (prop === 'width' || prop === 'availWidth') {
                // Round to common resolutions
                const width = Reflect.get(target, prop);
                return Math.round(width / 100) * 100;
            }
            if (prop === 'height' || prop === 'availHeight') {
                const height = Reflect.get(target, prop);
                return Math.round(height / 100) * 100;
            }
            return Reflect.get(target, prop);
        }
    });

    Object.defineProperty(window, 'screen', {
        get: () => screenProxy
    });

    // ========== Timezone Protection ==========

    // Override timezone offset if needed
    const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
    Date.prototype.getTimezoneOffset = function () {
        // Return offset matching configured timezone
        // This should be set based on the fingerprint profile
        return originalGetTimezoneOffset.call(this);
    };

    // ========== Connection Type Hiding ==========

    if (navigator.connection) {
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                downlink: 10,
                rtt: 50,
                saveData: false
            })
        });
    }

    console.log('[Privacy Cloak] ✓ Anti-detection measures active');

})();
