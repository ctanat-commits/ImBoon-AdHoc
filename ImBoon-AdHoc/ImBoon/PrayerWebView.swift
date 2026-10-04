import SwiftUI
import WebKit
import UIKit

struct PrayerWebView: UIViewRepresentable {
    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .default()
        let view = WKWebView(frame: .zero, configuration: config)
        view.navigationDelegate = context.coordinator
        view.uiDelegate = context.coordinator
        view.isOpaque = false
        view.backgroundColor = UIColor(red: 247/255, green: 245/255, blue: 239/255, alpha: 1)
        view.scrollView.backgroundColor = view.backgroundColor
        if let folder = Bundle.main.resourceURL?.appendingPathComponent("Web", isDirectory: true) {
            let index = folder.appendingPathComponent("index.html")
            context.coordinator.webRoot = folder.standardizedFileURL.path + "/"
            view.loadFileURL(index, allowingReadAccessTo: folder)
        }
        return view
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    final class Coordinator: NSObject, WKNavigationDelegate, WKUIDelegate {
        var webRoot = ""

        func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = action.request.url else { decisionHandler(.cancel); return }
            if url.isFileURL && url.standardizedFileURL.path.hasPrefix(webRoot) {
                decisionHandler(.allow)
            } else if url.scheme == "about" {
                decisionHandler(.allow)
            } else {
                decisionHandler(.cancel)
                openReference(url)
            }
        }

        func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
                     for action: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
            if action.targetFrame == nil, let url = action.request.url { openReference(url) }
            return nil
        }

        private func openReference(_ url: URL) {
            guard ["https", "http"].contains(url.scheme?.lowercased() ?? "") else { return }
            UIApplication.shared.open(url)
        }
    }
}
