// ContentView.swift
// Root layout: NavigationSplitView with sidebar + detail

import SwiftUI

struct ContentView: View {

    @EnvironmentObject var store: DocumentStore
    @State private var searchQuery = ""
    @State private var isSearching = false

    var body: some View {
        NavigationSplitView {
            SidebarView()
                .navigationSplitViewColumnWidth(min: 180, ideal: 220, max: 300)
        } detail: {
            if let doc = store.current {
                TextDetailView(doc: doc,
                               searchQuery: $searchQuery,
                               isSearching: $isSearching)
            } else {
                DropZoneView()
            }
        }
        .toolbar {
            ToolbarItemGroup(placement: .primaryAction) {
                Button {
                    store.presentOpenPanel()
                } label: {
                    Label("Open PDF", systemImage: "doc.badge.plus")
                }
                .keyboardShortcut("o", modifiers: .command)
                .help("Open PDF file(s)  ⌘O")

                Divider()

                Button {
                    store.copyCurrentText()
                } label: {
                    Label("Copy Text", systemImage: "doc.on.doc")
                }
                .disabled(store.current?.text.isEmpty ?? true)
                .help("Copy all extracted text  ⇧⌘C")
                .keyboardShortcut("c", modifiers: [.command, .shift])

                Button {
                    store.saveCurrentAsText()
                } label: {
                    Label("Save .txt", systemImage: "square.and.arrow.down")
                }
                .disabled(store.current == nil)
                .help("Save extracted text as .txt  ⌘S")

                Divider()

                Button {
                    withAnimation(.easeInOut(duration: 0.15)) {
                        isSearching.toggle()
                        if !isSearching { searchQuery = "" }
                    }
                } label: {
                    Label("Search", systemImage: isSearching ? "magnifyingglass.circle.fill" : "magnifyingglass")
                }
                .disabled(store.current == nil)
                .help("Search in text  ⌘F")
                .keyboardShortcut("f", modifiers: .command)
            }
        }
        // Accept dropped PDF files anywhere on the window
        .onDrop(of: [.pdf, .fileURL], isTargeted: nil) { providers in
            for provider in providers {
                provider.loadItem(forTypeIdentifier: "public.file-url", options: nil) { item, _ in
                    guard let data = item as? Data,
                          let url  = URL(dataRepresentation: data, relativeTo: nil),
                          url.pathExtension.lowercased() == "pdf"
                    else { return }
                    DispatchQueue.main.async { store.open(url: url) }
                }
            }
            return true
        }
    }
}

// ── Preview ───────────────────────────────────────────────────────────────────

#Preview {
    ContentView()
        .environmentObject(DocumentStore())
        .frame(width: 1100, height: 750)
}
