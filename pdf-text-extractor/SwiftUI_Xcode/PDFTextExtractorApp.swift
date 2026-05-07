// PDFTextExtractorApp.swift
// PDF Text Extractor — SwiftUI / PDFKit version
// Requires: macOS 13+, Xcode 14+, Swift 5.8+
// No external dependencies — uses Apple's built-in PDFKit.
//
// HOW TO USE:
//   1. Open Xcode → File → New → Project → macOS → App
//   2. Name it "PDFTextExtractor", set Interface to SwiftUI
//   3. Delete the auto-generated ContentView.swift
//   4. Drag all .swift files from this folder into the Xcode project
//   5. Build & Run (⌘R)

import SwiftUI

@main
struct PDFTextExtractorApp: App {

    @StateObject private var store = DocumentStore()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(store)
                .frame(minWidth: 900, minHeight: 600)
                .onOpenURL { url in
                    guard url.pathExtension.lowercased() == "pdf" else { return }
                    store.open(url: url)
                }
        }
        .commands {
            // Replace default New Window with Open PDF
            CommandGroup(replacing: .newItem) {
                Button("Open PDF…") { store.presentOpenPanel() }
                    .keyboardShortcut("o", modifiers: .command)
            }
            CommandGroup(after: .saveItem) {
                Button("Save as Text…") { store.saveCurrentAsText() }
                    .keyboardShortcut("s", modifiers: .command)
                    .disabled(store.current == nil)
            }
        }
        .windowStyle(.titleBar)
        .windowToolbarStyle(.unified(showsTitle: true))
    }
}
