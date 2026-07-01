---
id: licensing-trial-patterns
title: Licensing & Trial Patterns for Premiere Plugins
category: advanced
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2017"
min_premiere_version: "11.0"
api_namespace: null
languages: [javascript, jsx, python, shell]
tags: [licensing, trial-management, drm, activation, subscription, serialization]
related: [plugin-marketplace-strategies, security-deep-dive, best-practices]
sources: [
  "License management patterns",
  "Trial period implementations",
  "DRM and copy protection",
  "Subscription and activation systems"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Licensing & Trial Patterns for Premiere Plugins

## TL;DR

**Trial Period:** Free 14-30 day trial (no key needed). **Activation:** License key validated against server (API call, network required). **Offline Mode:** Cached license token (valid 30 days without internet). **DRM:** Use third-party service (Gumroad, License.io, SoftwareKey); avoid custom implementation. **Subscription:** Check license expiration on launch; warn 14 days before expiry. **Enforcement:** Graceful degradation (disabled features, watermark) instead of hard blocks. **Best Practice:** Balance UX (easy activation) with security (prevent sharing/piracy).

---

## Trial Period Implementation

### Simple Trial System

```javascript
function implementTrialPeriod(trialLengthDays) {
  /**
   * Free trial for N days (no license key needed)
   * Simplest approach for new plugins
   */
  
  var trial = {
    enabled: true,
    trialLength: trialLengthDays,
    startDate: null,
    endDate: null,
    daysRemaining: 0
  };
  
  function initializeTrial() {
    // First launch: set start date
    var settingsFile = new File(Folder.userData.absoluteURI + "/plugin_trial.json");
    
    if (!settingsFile.exists) {
      // First run: start trial
      trial.startDate = new Date();
      trial.endDate = new Date(trial.startDate.getTime() + (trialLengthDays * 24 * 60 * 60 * 1000));
      
      var settings = {
        trialStart: trial.startDate.toISOString(),
        trialEnd: trial.endDate.toISOString()
      };
      
      settingsFile.open("w");
      settingsFile.write(JSON.stringify(settings));
      settingsFile.close();
      
      $.writeln("Trial started: " + trial.startDate);
      $.writeln("Trial ends: " + trial.endDate);
      
    } else {
      // Subsequent run: check trial status
      settingsFile.open("r");
      var settings = JSON.parse(settingsFile.read());
      settingsFile.close();
      
      trial.startDate = new Date(settings.trialStart);
      trial.endDate = new Date(settings.trialEnd);
    }
    
    // Calculate days remaining
    var now = new Date();
    var timeRemaining = trial.endDate.getTime() - now.getTime();
    trial.daysRemaining = Math.ceil(timeRemaining / (24 * 60 * 60 * 1000));
    
    return trial;
  }
  
  $.writeln("=== TRIAL PERIOD IMPLEMENTATION ===\n");
  
  var trialStatus = initializeTrial();
  
  $.writeln("Status:");
  $.writeln("Trial Started: " + trialStatus.startDate);
  $.writeln("Trial Ends: " + trialStatus.endDate);
  $.writeln("Days Remaining: " + trialStatus.daysRemaining);
  $.writeln("");
  
  if (trialStatus.daysRemaining > 3) {
    $.writeln("Status: Active trial ✓");
  } else if (trialStatus.daysRemaining > 0) {
    $.writeln("Status: ⚠ Trial expires in " + trialStatus.daysRemaining + " day(s)");
    $.writeln("→ Show upgrade prompt");
  } else {
    $.writeln("Status: ✗ Trial expired");
    $.writeln("→ Disable features, prompt for license key");
  }
  
  return trialStatus;
}

// Usage
implementTrialPeriod(30);  // 30-day free trial
```

---

## License Key Validation

### Validate License Server

```javascript
function validateLicenseKey(licenseKey) {
  /**
   * Validate license key against server
   * Recommended: Use third-party license service
   */
  
  $.writeln("=== LICENSE KEY VALIDATION ===\n");
  
  $.writeln("Method 1: Local Validation (Not Recommended)");
  $.writeln("- Verify key format locally");
  $.writeln("- Downside: Key can be brute-forced");
  $.writeln("- Risk: Piracy (keys easily shared)");
  $.writeln("");
  
  $.writeln("Method 2: Server Validation (Recommended)");
  $.writeln("- Send key to license server");
  $.writeln("- Server validates & returns status");
  $.writeln("- Cache result locally (30 days offline)");
  $.writeln("- On expiry, validate online again");
  $.writeln("");
  
  $.writeln("Implementation (Server Validation):");
  $.writeln("1. User enters license key in plugin panel");
  $.writeln("2. Plugin calls: POST /api/validate");
  $.writeln("   {");
  $.writeln('     \"licenseKey\": \"ABC-123-XYZ\",');
  $.writeln('     \"pluginId\": \"my-plugin-v1\",');
  $.writeln('     \"machineId\": \"hash(MAC+CPU+HDD)\"');
  $.writeln("   }");
  $.writeln("3. Server returns:");
  $.writeln("   {");
  $.writeln('     \"valid\": true,');
  $.writeln('     \"expiresAt\": \"2026-12-31\",');
  $.writeln('     \"features\": [\"basic\", \"advanced\"]');
  $.writeln("   }");
  $.writeln("4. Cache response locally with timestamp");
  $.writeln("5. On next launch, check cache validity");
  $.writeln("");
  
  $.writeln("Third-Party Services (Recommended):");
  $.writeln("- Gumroad: Integrated license validation");
  $.writeln("- License.io: Dedicated license server");
  $.writeln("- SoftwareKey: License + DRM");
  $.writeln("- Fastspring: Payment + license processing");
  $.writeln("");
  
  $.writeln("Offline Support:");
  $.writeln("- Cache license token for 30 days");
  $.writeln("- Allow offline use if last validation < 30 days ago");
  $.writeln("- Revalidate on next internet connection");
  $.writeln("- Clear cache if validation fails (revoked license)");
  
  return { valid: false, method: "server", cacheExpiry: 30 };
}

// Usage
validateLicenseKey("ABC-123-XYZ-789");
```

### Implement License Caching

```javascript
function cacheLicenseTokenOffline(licenseData, cacheDurationDays) {
  /**
   * Cache license validation result locally
   * Allows offline operation within cache period
   */
  
  var cache = {
    licenseKey: licenseData.key,
    validatedAt: new Date().toISOString(),
    expiresAt: licenseData.expiresAt,
    cacheExpiry: new Date(new Date().getTime() + (cacheDurationDays * 24 * 60 * 60 * 1000)),
    features: licenseData.features,
    machineId: generateMachineId()
  };
  
  function generateMachineId() {
    // Generate unique machine identifier
    // Use: MAC address + CPU serial + HDD identifier
    // Hash to avoid privacy concerns
    return "machine_hash_xyz";  // Placeholder
  }
  
  function saveCacheToFile() {
    var cacheFile = new File(Folder.userData.absoluteURI + "/license_cache.json");
    var encrypted = encryptLicenseCache(JSON.stringify(cache));
    
    cacheFile.open("w");
    cacheFile.write(encrypted);
    cacheFile.close();
  }
  
  function encryptLicenseCache(data) {
    // Encrypt with plugin ID as key
    // Prevents user from transferring license between machines
    return data;  // Placeholder
  }
  
  $.writeln("=== LICENSE CACHE MANAGEMENT ===\n");
  
  $.writeln("Cache Strategy:");
  $.writeln("1. Validate license on server (online)");
  $.writeln("2. Cache result locally (encrypted)");
  $.writeln("3. On next launch, check cache validity:");
  $.writeln("   a. If cache valid: Use cached license");
  $.writeln("   b. If cache expired: Require online validation");
  $.writeln("4. Periodically revalidate (every 30 days)");
  $.writeln("");
  
  $.writeln("Cache Contents:");
  $.writeln("- License key (encrypted)");
  $.writeln("- Validated at (timestamp)");
  $.writeln("- Expires at (license expiration)");
  $.writeln("- Cache expiry (when to revalidate)");
  $.writeln("- Features (enabled features)");
  $.writeln("- Machine ID (prevent license sharing)");
  $.writeln("");
  
  $.writeln("Security Considerations:");
  $.writeln("✓ Encrypt cache file (AES-256)");
  $.writeln("✓ Include machine ID (tied to hardware)");
  $.writeln("✓ Time-limit cache (max 30 days offline)");
  $.writeln("✓ Detect cache tampering (checksum)");
  $.writeln("✓ Clear cache if validation fails");
  $.writeln("");
  
  $.writeln("User Experience:");
  $.writeln("✓ Works offline (up to 30 days)");
  $.writeln("✓ Seamless activation (no friction)");
  $.writeln("✓ Clear warnings (expiration approaching)");
  $.writeln("✓ Graceful degradation (features disabled)");
  
  saveCacheToFile();
  
  return cache;
}

// Usage
cacheLicenseTokenOffline({
  key: "ABC-123-XYZ",
  expiresAt: "2026-12-31",
  features: ["basic", "advanced"]
}, 30);
```

---

## Subscription & License Expiry

### Handle Subscription Expiration

```javascript
function handleSubscriptionExpiry() {
  /**
   * Monitor subscription expiration, warn users in advance
   */
  
  $.writeln("=== SUBSCRIPTION EXPIRY HANDLING ===\n");
  
  $.writeln("Expiry Monitoring Workflow:");
  $.writeln("1. Load license from cache/server");
  $.writeln("2. Check expiry date:");
  $.writeln("");
  
  $.writeln("   If expires > 14 days:");
  $.writeln("   ✓ Full functionality");
  $.writeln("   (silent, no warning)");
  $.writeln("");
  
  $.writeln("   If expires in 3-14 days:");
  $.writeln("   ⚠ Show banner");
  $.writeln('   \"Your license expires in N days\"');
  $.writeln('   Button: \"Renew Now\" → opens browser to renew page');
  $.writeln("   Features: Fully enabled (grace period)");
  $.writeln("");
  
  $.writeln("   If expires in 0-3 days:");
  $.writeln("   ⚠⚠ Show prominent warning");
  $.writeln('   \"License expires soon! Renew to keep using plugin\"');
  $.writeln("   Features: Fully enabled (but show warning every launch)");
  $.writeln("");
  
  $.writeln("   If expired:");
  $.writeln("   ✗✗ Disable features gracefully");
  $.writeln("   Options:");
  $.writeln("   a) Watermark output (but allow use)");
  $.writeln("   b) Disable advanced features (keep basic)");
  $.writeln("   c) Force purchase (strongest enforcement)");
  $.writeln("   d) Trial mode (limited functionality)");
  $.writeln("");
  
  $.writeln("Implementation:");
  $.writeln("function checkSubscriptionStatus() {");
  $.writeln("  var license = loadLicense();");
  $.writeln("  var expiryDate = new Date(license.expiresAt);");
  $.writeln("  var daysUntilExpiry = (expiryDate - new Date()) / (1000*60*60*24);");
  $.writeln("");
  $.writeln("  if (daysUntilExpiry > 14) {");
  $.writeln("    // OK: no warning");
  $.writeln("  } else if (daysUntilExpiry > 3) {");
  $.writeln("    showExpiryWarningBanner(daysUntilExpiry);");
  $.writeln("  } else if (daysUntilExpiry > 0) {");
  $.writeln("    showUrgentExpiryWarning();");
  $.writeln("  } else {");
  $.writeln("    disableFeatures();  // Expired");
  $.writeln("    showRenewalPrompt();");
  $.writeln("  }");
  $.writeln("}");
  $.writeln("");
  
  $.writeln("Best Practice: Graceful Degradation");
  $.writeln("- Keep plugin functional (avoid hard blocks)");
  $.writeln("- Add watermark or limitation instead of disabling");
  $.writeln("- Examples:");
  $.writeln("  ✓ Disable advanced features, keep basic");
  $.writeln("  ✓ Add watermark to output (visible but usable)");
  $.writeln("  ✓ Limit export resolution (1080p max instead of 4K)");
  $.writeln("  ✗ Hard block (completely disable plugin)");
  
  return { gracefulDegradation: true };
}

// Usage
handleSubscriptionExpiry();
```

---

## Feature Flag Management

### Conditional Features Based on License

```javascript
function manageFeatureFlagsPerLicense(license) {
  /**
   * Enable/disable features based on license tier
   */
  
  var featureMatrix = {
    free: {
      basicEditing: true,
      advancedEffects: false,
      batchProcessing: false,
      cloudSync: false,
      prioritySupport: false
    },
    pro: {
      basicEditing: true,
      advancedEffects: true,
      batchProcessing: false,
      cloudSync: false,
      prioritySupport: false
    },
    premium: {
      basicEditing: true,
      advancedEffects: true,
      batchProcessing: true,
      cloudSync: true,
      prioritySupport: true
    }
  };
  
  $.writeln("=== FEATURE FLAG MANAGEMENT ===\n");
  
  $.writeln("License Tiers:");
  $.writeln("");
  
  for (var tier in featureMatrix) {
    var features = featureMatrix[tier];
    $.writeln(tier.toUpperCase() + ":");
    
    for (var feature in features) {
      var enabled = features[feature];
      var icon = enabled ? "✓" : "✗";
      $.writeln("  " + icon + " " + feature);
    }
    $.writeln("");
  }
  
  $.writeln("Implementation:");
  $.writeln("function isFeatureEnabled(feature) {");
  $.writeln("  var license = loadLicense();");
  $.writeln("  var tier = license.tier;  // 'free', 'pro', 'premium'");
  $.writeln("  var features = featureMatrix[tier];");
  $.writeln("  return features[feature] || false;");
  $.writeln("}");
  $.writeln("");
  $.writeln("// Usage:");
  $.writeln("if (isFeatureEnabled('batchProcessing')) {");
  $.writeln("  // Show batch processing UI");
  $.writeln("} else {");
  $.writeln("  // Show 'Upgrade to Pro' button");
  $.writeln("}");
  $.writeln("");
  
  $.writeln("UX Best Practices:");
  $.writeln("- Gray out disabled features (show they exist)");
  $.writeln("- Include 'Upgrade' button on locked features");
  $.writeln("- Offer trial of premium features (time-limited)");
  $.writeln("- Never hide features (let users see what they're missing)");
  $.writeln("- Show clear upgrade path (which tier enables feature)");
  
  return featureMatrix;
}

// Usage
manageFeatureFlagsPerLicense({ tier: "pro" });
```

---

## Piracy Prevention

### Anti-Piracy Strategy

```javascript
function implementAntiPiracyMeasures() {
  /**
   * Strategies to prevent license sharing and piracy
   */
  
  $.writeln("=== ANTI-PIRACY MEASURES ===\n");
  
  $.writeln("Machine ID Binding:");
  $.writeln("- Generate unique ID from: MAC address + CPU + HDD");
  $.writeln("- Hash to avoid privacy issues");
  $.writeln("- Tie license to specific machine");
  $.writeln("- License won't work if transferred to another computer");
  $.writeln("- Pro: High piracy prevention");
  $.writeln("- Con: Users can't move license between computers");
  $.writeln("");
  
  $.writeln("License Key Format:");
  $.writeln("- Use strong format: XXXXXXXX-XXXXXXXX-XXXXXXXX");
  $.writeln("- Include checksum (prevent modification)");
  $.writeln("- Include version (prevent using old keys)");
  $.writeln("- Include machine hash (prevent sharing)");
  $.writeln("");
  
  $.writeln("Telemetry & Monitoring:");
  $.writeln("✓ Track license usage (anonymously)");
  $.writeln("✓ Detect unusual patterns:");
  $.writeln("  - Same key on 100+ different machines");
  $.writeln("  - Multiple concurrent logins");
  $.writeln("  - Rapid geographic changes");
  $.writeln("✓ Revoke suspicious licenses");
  $.writeln("✓ Warn legitimate users (grace period before revocation)");
  $.writeln("");
  
  $.writeln("Don't Over-Engineer:");
  $.writeln("- Aggressive DRM frustrates legitimate users");
  $.writeln("- Determined pirates will crack anything");
  $.writeln("- Focus on: Ease of purchase > Piracy prevention");
  $.writeln("- Offer: Fair pricing, easy licensing, good support");
  $.writeln("- Result: Users prefer buying over pirating");
  $.writeln("");
  
  $.writeln("Legal Approach:");
  $.writeln("- Include clear license terms in EULA");
  $.writeln("- Document what user can/can't do");
  $.writeln("- Pursue copyright infringement (when egregious)");
  $.writeln("- Most effective: Community enforcement (bad reputation)");
  
  return { approach: "balanced", overEngineer: false };
}

// Usage
implementAntiPiracyMeasures();
```

---

## Licensing Checklist

- ☐ Decide on trial period length (14-30 days typical)
- ☐ Choose licensing service (Gumroad, License.io, or custom)
- ☐ Implement license key validation (server-based)
- ☐ Cache license token for offline use (30 days)
- ☐ Add subscription expiry checks on launch
- ☐ Define feature tiers (free, pro, premium, enterprise)
- ☐ Implement graceful degradation (not hard blocks)
- ☐ Show expiry warnings (14 days, 3 days, 0 days)
- ☐ Bind license to machine ID (prevent sharing)
- ☐ Include license terms in EULA
- ☐ Monitor for suspicious license usage
- ☐ Provide easy upgrade/renewal path
- ☐ Document license activation process
- ☐ Test offline license validation
- ☐ Plan revocation strategy (compromised licenses)

---

## See Also

- Knowledge/plugin-marketplace-strategies.md — Distribution and marketing
- Knowledge/security-deep-dive.md — License encryption and security
- Knowledge/best-practices.md — Code quality standards
- Knowledge/panel-development-uxp.md — UXP panel development

---

## Sources

- Gumroad Licensing: https://help.gumroad.com/
- License.io: https://license.io/
- SoftwareKey: https://www.softwarekey.com/
- Fastspring: https://www.fastspring.com/
- EULA Best Practices: https://www.termshub.com/eula-generator
