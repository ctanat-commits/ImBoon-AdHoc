import SwiftUI

@main
struct ImBoonApp: App {
    var body: some Scene {
        WindowGroup {
            PrayerWebView()
                .background(Color(red: 247/255, green: 245/255, blue: 239/255))
                .ignoresSafeArea(.container, edges: .bottom)
        }
    }
}
