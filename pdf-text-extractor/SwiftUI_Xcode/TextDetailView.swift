// TextDetailView.swift
// Right panel: extracted text with search bar and match highlighting

import SwiftUI

struct TextDetailView: View {

    @ObservedObject var doc: PDFFile
    @Binding var searchQuery: String
    @Binding var isSearching: Bool

    @State private var matchCount = 0

    var body: some View {
        VStack(spacing: 0) {

            // ── Search bar ────────────────────────────────────────────────
            if isSearching {
                HStack(spacing: 10) {
                    Image(systemName: "magnifyingglass")
                        .foregroundStyle(.secondary)

                    TextField("Search in text…", text: $searchQuery)
                        .textFieldStyle(.plain)
                        .font(.system(size: 13))
                        .onSubmit { /* next match — future enhancement */ }

                    if !searchQuery.isEmpty {
                        Text(matchCount == 0
                             ? "No matches"
                             : "\(matchCount) match\(matchCount == 1 ? "" : "es")")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                            .frame(minWidth: 80, alignment: .trailing)
                    }

                    Button {
                        searchQuery = ""
                        withAnimation(.easeInOut(duration: 0.15)) {
                            isSearching = false
                        }
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                    }
                    .buttonStyle(.plain)
                    .keyboardShortcut(.escape, modifiers: [])
                }
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(.bar)
                .overlay(alignment: .bottom) {
                    Divider()
                }
            }

            // ── Text content ──────────────────────────────────────────────
            if doc.isLoading {
                Spacer()
                ProgressView("Extracting text…")
                    .progressViewStyle(.circular)
                Spacer()

            } else if let err = doc.error {
                Spacer()
                VStack(spacing: 12) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 40))
                        .foregroundStyle(.orange)
                    Text("Could not extract text")
                        .font(.headline)
                    Text(err)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding()
                Spacer()

            } else {
                HighlightedTextView(
                    text:       doc.text,
                    query:      searchQuery,
                    matchCount: $matchCount
                )
            }

            // ── Status bar ────────────────────────────────────────────────
            HStack {
                Text(doc.statusLine)
                    .font(.system(size: 11))
                    .foregroundStyle(.secondary)
                Spacer()
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 5)
            .background(.bar)
            .overlay(alignment: .top) { Divider() }
        }
        .navigationTitle(doc.name)
        .navigationSubtitle(doc.isLoading ? "Loading…"
                            : "\(doc.pageCount) page\(doc.pageCount == 1 ? "" : "s")")
    }
}

// ── NSTextView bridge for smooth, searchable large-text rendering ─────────────

struct HighlightedTextView: NSViewRepresentable {

    let text      : String
    let query     : String
    @Binding var matchCount: Int

    func makeNSView(context: Context) -> NSScrollView {
        let scroll    = NSScrollView()
        let textView  = NSTextView()

        textView.isEditable           = false
        textView.isSelectable         = true
        textView.isRichText           = false
        textView.drawsBackground      = false
        textView.textContainerInset   = NSSize(width: 28, height: 20)
        textView.font                 = .systemFont(ofSize: 13)
        textView.autoresizingMask     = [.width]
        textView.isVerticallyResizable = true

        scroll.documentView          = textView
        scroll.hasVerticalScroller   = true
        scroll.hasHorizontalScroller = false
        scroll.autohidesScrollers    = true
        scroll.drawsBackground       = false
        scroll.backgroundColor       = .clear

        context.coordinator.textView = textView
        return scroll
    }

    func updateNSView(_ scrollView: NSScrollView, context: Context) {
        let tv = context.coordinator.textView!

        // Only reset full string if text changed
        if tv.string != text {
            tv.string = text
        }

        // Apply search highlights
        guard let storage = tv.textStorage else { return }
        storage.removeAttribute(.backgroundColor, range: NSRange(text.startIndex..., in: text))
        storage.removeAttribute(.foregroundColor, range: NSRange(text.startIndex..., in: text))

        guard !query.isEmpty else {
            DispatchQueue.main.async { matchCount = 0 }
            return
        }

        var count     = 0
        var searchRange = text.startIndex ..< text.endIndex

        while let range = text.range(of: query,
                                     options: [.caseInsensitive, .diacriticInsensitive],
                                     range: searchRange) {
            let nsRange = NSRange(range, in: text)
            storage.addAttribute(.backgroundColor,
                                 value: NSColor.systemYellow.withAlphaComponent(0.7),
                                 range: nsRange)
            storage.addAttribute(.foregroundColor,
                                 value: NSColor.black,
                                 range: nsRange)
            count += 1
            searchRange = range.upperBound ..< text.endIndex
        }

        DispatchQueue.main.async { matchCount = count }

        // Scroll to first match
        if count > 0, let firstRange = text.range(of: query,
                                                   options: [.caseInsensitive, .diacriticInsensitive]) {
            let ns = NSRange(firstRange, in: text)
            tv.scrollRangeToVisible(ns)
        }
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    final class Coordinator {
        weak var textView: NSTextView?
    }
}

// ── Drop zone (shown when no document selected) ───────────────────────────────

struct DropZoneView: View {
    @EnvironmentObject var store: DocumentStore

    var body: some View {
        VStack(spacing: 14) {
            Spacer(minLength: 60)
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 64, weight: .ultraLight))
                .foregroundStyle(.tertiary)

            Text("Drop PDF files here")
                .font(.title2.weight(.medium))

            Text("…or click Open PDF in the toolbar above")
                .font(.callout)
                .foregroundStyle(.secondary)

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .contentShape(Rectangle())
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
