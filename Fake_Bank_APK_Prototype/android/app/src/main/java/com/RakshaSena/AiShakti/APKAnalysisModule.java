package com.RakshaSena.AiShakti;
package com.RakshaSena;

import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.util.Base64;
import android.util.Log;

import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.bridge.Arguments;

import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;

public class APKAnalysisModule extends ReactContextBaseJavaModule {
    private static final String TAG = "APKAnalysisModule";
    private final ReactApplicationContext reactContext;

    public APKAnalysisModule(ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
    }

    @Override
    public String getName() {
        return "APKAnalysisModule";
    }

    @ReactMethod
    public void extractAPKMetadata(String filePath, Promise promise) {
        try {
            PackageManager pm = reactContext.getPackageManager();
            PackageInfo packageInfo = pm.getPackageArchiveInfo(filePath, PackageManager.GET_SIGNATURES);
            
            if (packageInfo != null) {
                WritableMap result = Arguments.createMap();
                
                // Extract package name
                result.putString("packageName", packageInfo.packageName);
                
                // Extract version info
                result.putString("versionName", packageInfo.versionName);
                result.putInt("versionCode", packageInfo.versionCode);
                
                // Extract signatures
                Signature[] signatures = packageInfo.signatures;
                List<String> signatureList = new ArrayList<>();
                
                for (Signature signature : signatures) {
                    MessageDigest md = MessageDigest.getInstance("SHA-256");
                    md.update(signature.toByteArray());
                    String signatureHash = Base64.encodeToString(md.digest(), Base64.DEFAULT);
                    signatureList.add(signatureHash);
                }
                
                result.putArray("signatures", Arguments.fromArray(signatureList.toArray(new String[0])));
                
                promise.resolve(result);
            } else {
                promise.reject("ANALYSIS_ERROR", "Failed to analyze APK");
            }
        } catch (Exception e) {
            Log.e(TAG, "APK analysis error", e);
            promise.reject("ANALYSIS_ERROR", e.getMessage());
        }
    }

    @ReactMethod
    public void getCertificateInfo(String filePath, Promise promise) {
        try {
            PackageManager pm = reactContext.getPackageManager();
            PackageInfo packageInfo = pm.getPackageArchiveInfo(filePath, PackageManager.GET_SIGNATURES);
            
            if (packageInfo != null && packageInfo.signatures != null && packageInfo.signatures.length > 0) {
                Signature signature = packageInfo.signatures[0];
                
                // Get certificate information
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                md.update(signature.toByteArray());
                String certHash = Base64.encodeToString(md.digest(), Base64.NO_WRAP);
                
                // For SHA-1
                MessageDigest mdSha1 = MessageDigest.getInstance("SHA-1");
                mdSha1.update(signature.toByteArray());
                String certHashSha1 = Base64.encodeToString(mdSha1.digest(), Base64.NO_WRAP);
                
                WritableMap result = Arguments.createMap();
                result.putString("sha256", certHash);
                result.putString("sha1", certHashSha1);
                result.putString("algorithm", "SHA256withRSA"); // Most common
                
                promise.resolve(result);
            } else {
                promise.reject("CERT_ERROR", "No certificate found");
            }
        } catch (Exception e) {
            Log.e(TAG, "Certificate analysis error", e);
            promise.reject("CERT_ERROR", e.getMessage());
        }
    }

    @ReactMethod
    public void checkPermissions(String filePath, Promise promise) {
        try {
            PackageManager pm = reactContext.getPackageManager();
            PackageInfo packageInfo = pm.getPackageArchiveInfo(filePath, PackageManager.GET_PERMISSIONS);
            
            if (packageInfo != null && packageInfo.requestedPermissions != null) {
                WritableMap result = Arguments.createMap();
                
                // Get all permissions
                result.putArray("permissions", Arguments.fromArray(packageInfo.requestedPermissions));
                
                // Check for dangerous permissions
                String[] dangerousPermissions = {
                    "android.permission.READ_SMS",
                    "android.permission.RECEIVE_SMS",
                    "android.permission.SEND_SMS",
                    "android.permission.READ_CONTACTS",
                    "android.permission.WRITE_CONTACTS",
                    "android.permission.ACCESS_FINE_LOCATION",
                    "android.permission.ACCESS_COARSE_LOCATION",
                    "android.permission.CAMERA",
                    "android.permission.RECORD_AUDIO",
                    "android.permission.READ_PHONE_STATE",
                    "android.permission.CALL_PHONE"
                };
                
                List<String> dangerousFound = new ArrayList<>();
                for (String perm : packageInfo.requestedPermissions) {
                    for (String dangerousPerm : dangerousPermissions) {
                        if (perm.equals(dangerousPerm)) {
                            dangerousFound.add(perm);
                            break;
                        }
                    }
                }
                
                result.putArray("dangerousPermissions", Arguments.fromArray(dangerousFound.toArray(new String[0])));
                result.putInt("dangerousCount", dangerousFound.size());
                
                promise.resolve(result);
            } else {
                promise.reject("PERMISSION_ERROR", "No permissions found or error reading APK");
            }
        } catch (Exception e) {
            Log.e(TAG, "Permission analysis error", e);
            promise.reject("PERMISSION_ERROR", e.getMessage());
        }
    }
}