// DocumentStore.swift
// Observable model layer — holds all loaded PDFs and coordinates UI state.

import SwiftUI
import PDFKit
import AppKit
import Combine
import UniformTypeIdentifiers

// ── Single PDF Document ───────────────────────────────────────────────────────

@MainActor
final class PDFFile: ObservableObject, Identifiable {

    let id   = UUID()
    let url  : URL
    var name : String { url.lastPathComponent }

    @Published var text      : String      = ""
    @Published var pageCount : Int         = 0
    @Published var isLoading : Bool        = true
    @Published var error     : String?

    var statusLine: String {
        if isLoading { return "\(name)  ·  Loading…" }
        if let e = error { return "\(name)  ·  ⚠ \(e)" }
        let p = pageCount == 1 ? "1 page" : "\(pageCount) pages"
        let c = text.count.formatted() + " chars"
        return "\(name)  ·  \(p)  ·  \(c)"
    }

    init(url: URL) {
        self.url = url
        Task.detached(priority: .userInitiated) { [weak self] in
            guard let self else { return }
            await self.load()
        }
    }

    private func load() async {
        guard let doc = PDFDocument(url: url) else {
            await MainActor.run {
                self.error = "Could not open PDF"
                self.isLoading = false
            }
            return
        }

        let pages    = doc.pageCount
        var parts    = [String]()

        for i in 0 ..< pages {
            guard let page = doc.page(at: i) else { continue }
            let raw = page.string ?? ""
            if !raw.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                parts.append("── Page \(i + 1) of \(pages) ──\n\n\(raw)")
            }
        }

        let full = parts.isEmpty
            ? "(No extractable text found in this PDF.)"
            : parts.joined(separator: "\n\n\n")

        await MainActor.run {
            self.text      = full
            self.pageCount = pages
            self.isLoading = false
        }
    }
}

// ── Document Store ────────────────────────────────────────────────────────────

@MainActor
final class DocumentStore: ObservableObject {

    @Published var documents  : [PDFFile]   = []
    @Published var currentID  : UUID?

    var current: PDFFile? {
        guard let id = currentID else { return nil }
        return documents.first(where: { $0.id == id })
    }

    // ── Open ──────────────────────────────────────────────────────────────────

    func presentOpenPanel() {
        let panel = NSOpenPanel()
        panel.title            = "Open PDF Files"
        panel.allowsMultipleSelection = true
        panel.canChooseDirectories    = false
        panel.allowedContentTypes     = [UTType.pdf]

        guard panel.runModal() == .OK else { return }
        for url in panel.urls { open(url: url) }
    }

    func open(url: URL) {
        let abs = url.standardizedFileURL
        guard !documents.contains(where: { $0.url.standardizedFileURL == abs }) else { return }
        let doc = PDFFile(url: abs)
        documents.append(doc)
        currentID = doc.id
    }

    // ── Remove ────────────────────────────────────────────────────────────────

    func remove(_ doc: PDFFile) {
        if currentID == doc.id {
            // Select adjacent document
            if let idx = documents.firstIndex(where: { $0.id == doc.id }) {
                let nextIdx = idx < documents.count - 1 ? idx + 1 : idx - 1
                currentID = nextIdx >= 0 ? documents[nextIdx].id : nil
            }
        }
        documents.removeAll(where: { $0.id == doc.id })
    }

    // ── Save as Text ──────────────────────────────────────────────────────────

    func saveCurrentAsText() {
        guard let doc = current, !doc.text.isEmpty else { return }

        let panel              = NSSavePanel()
        panel.title            = "Save Extracted Text"
        panel.nameFieldStringValue = doc.url.deletingPathExtension().appendingPathExtension("txt").lastPathComponent
        panel.allowedContentTypes  = [UTType.plainText]

        guard panel.runModal() == .OK, let dest = panel.url else { return }
        try? doc.text.write(to: dest, atomically: true, encoding: .utf8)
    }

    // ── Copy ──────────────────────────────────────────────────────────────────

    func copyCurrentText() {
        guard let text = current?.text else { return }
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(text, forType: .string)
    }
}
