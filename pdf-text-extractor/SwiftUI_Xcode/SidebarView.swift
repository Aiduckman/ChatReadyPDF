// SidebarView.swift
// Left panel: list of all open PDF documents

import SwiftUI

struct SidebarView: View {

    @EnvironmentObject var store: DocumentStore

    var body: some View {
        List(store.documents, selection: $store.currentID) { doc in
            SidebarRow(doc: doc)
                .tag(doc.id)
                .contextMenu {
                    Button("Show in Finder") { revealInFinder(doc) }
                    Divider()
                    Button("Remove", role: .destructive) { store.remove(doc) }
                }
        }
        .listStyle(.sidebar)
        .navigationTitle("PDFs")
        .overlay {
            if store.documents.isEmpty {
                Text("No PDFs open")
                    .font(.callout)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private func revealInFinder(_ doc: PDFFile) {
        NSWorkspace.shared.activateFileViewerSelecting([doc.url])
    }
}

// ── Single row ────────────────────────────────────────────────────────────────

struct SidebarRow: View {

    @ObservedObject var doc: PDFFile

    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: doc.error != nil ? "exclamationmark.triangle.fill"
                                               : "doc.text.fill")
                .foregroundStyle(doc.error != nil ? .red : .accentColor)
                .font(.system(size: 14, weight: .medium))
                .frame(width: 20)

            VStack(alignment: .leading, spacing: 2) {
                Text(doc.name)
                    .lineLimit(2)
                    .font(.system(size: 13, weight: .medium))

                if doc.isLoading {
                    ProgressView()
                        .scaleEffect(0.5)
                        .frame(height: 12)
                } else if let e = doc.error {
                    Text(e)
                        .font(.caption)
                        .foregroundStyle(.red)
                        .lineLimit(1)
                } else {
                    Text("\(doc.pageCount) page\(doc.pageCount == 1 ? "" : "s")")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding(.vertical, 2)
    }
}
