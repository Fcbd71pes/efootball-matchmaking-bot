package com.example.efootballadmin

import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.example.efootballadmin.theme.EFootballAdminTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize Python and bootstrap in a background thread
        Thread {
            try {
                if (!Python.isStarted()) {
                    Python.start(AndroidPlatform(this))
                }
                val py = Python.getInstance()
                val bootstrap = py.getModule("bootstrap")
                bootstrap.callAttr("run")
            } catch (e: java.lang.Exception) {
                e.printStackTrace()
            }
        }.start()
        
        enableEdgeToEdge()
        setContent {
            EFootballAdminTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    AppScreen(this)
                }
            }
        }
    }
}

class WebAppInterface(private val activity: ComponentActivity) {
    @android.webkit.JavascriptInterface
    fun callPython(path: String, argsJson: String): String {
        return try {
            val py = Python.getInstance()
            val adminPanel = py.getModule("admin_panel")
            val handler = adminPanel.get("handle_request")
            val result = handler?.call(path, argsJson)
            result?.toString() ?: "{\"status\":\"error\", \"detail\":\"handle_request not found\"}"
        } catch (e: Exception) {
            e.printStackTrace()
            "{\"status\":\"error\", \"detail\":\"${e.message}\"}"
        }
    }
}

@Composable
fun AppScreen(activity: ComponentActivity) {
    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                WebView(ctx).apply {
                    webViewClient = object : WebViewClient() {
                        override fun onReceivedError(
                            view: WebView?,
                            request: WebResourceRequest?,
                            error: WebResourceError?
                        ) {
                            // Local files loaded from assets will not hit connection errors
                        }

                        override fun shouldInterceptRequest(
                            view: WebView?,
                            request: WebResourceRequest?
                        ): WebResourceResponse? {
                            val url = request?.url?.toString() ?: ""
                            if (url.startsWith("https://appassets.androidplatform.net/")) {
                                return try {
                                    val uri = android.net.Uri.parse(url)
                                    val path = uri.path?.removePrefix("/") ?: ""
                                    val stream = ctx.assets.open(path)
                                    val mimeType = when {
                                        path.endsWith(".html") -> "text/html"
                                        path.endsWith(".css") -> "text/css"
                                        path.endsWith(".js") -> "application/javascript"
                                        path.endsWith(".png") -> "image/png"
                                        path.endsWith(".jpg") || path.endsWith(".jpeg") -> "image/jpeg"
                                        else -> "text/plain"
                                    }
                                    WebResourceResponse(mimeType, "UTF-8", stream)
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                    null
                                }
                            }
                            return super.shouldInterceptRequest(view, request)
                        }
                    }
                    settings.javaScriptEnabled = true
                    settings.domStorageEnabled = true
                    settings.useWideViewPort = true
                    settings.loadWithOverviewMode = true
                    settings.allowFileAccess = true
                    settings.allowContentAccess = true
                    
                    addJavascriptInterface(WebAppInterface(activity), "AndroidBridge")
                    loadUrl("https://appassets.androidplatform.net/templates/index.html")
                }
            },
            modifier = Modifier.fillMaxSize()
        )
    }
}

