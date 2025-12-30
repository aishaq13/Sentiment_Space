"""
Swift main app entry point for Sentiment Space iOS app.
Exported as Swift code.
"""

swift_app = """
import SwiftUI

@main
struct SentimentSpaceApp: App {
    var body: some Scene {
        WindowGroup {
            HomeView()
                .preferredColorScheme(nil) // Support both light and dark mode
        }
    }
}

/* 
SENTIMENT SPACE iOS APP
Privacy-first thought analysis

Architecture:
- MVVM pattern with @StateObject view models
- Local persistence with Swift Foundation
- Async/await for network requests
- Clean separation between UI and services

Features:
- Input new thoughts
- View summaries and sentiment
- Browse history locally
- Optional export to S3 (via backend)

Privacy:
- All data stored locally
- No automatic cloud sync
- Opt-in export only
- Works completely offline
*/
"""
