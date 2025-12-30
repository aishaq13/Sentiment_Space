"""
Swift UI Views for displaying analysis results.
Exported as Swift code.
"""

swift_summary_view = """
import SwiftUI

// MARK: - Summary View

struct SummaryView: View {
    let thought: Thought
    
    var sentimentColor: Color {
        switch thought.sentiment?.lowercased() {
        case "positive":
            return .green
        case "negative":
            return .red
        default:
            return .gray
        }
    }
    
    var sentimentEmoji: String {
        switch thought.sentiment?.lowercased() {
        case "positive":
            return "😊"
        case "negative":
            return "😟"
        default:
            return "😐"
        }
    }
    
    var body: some View {
        VStack(spacing: 16) {
            // Original Text
            VStack(alignment: .leading, spacing: 8) {
                Text("Original Thought")
                    .font(.headline)
                
                Text(thought.rawText)
                    .font(.body)
                    .padding(12)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)
            }
            
            // Summary
            if let summary = thought.summary {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Summary")
                        .font(.headline)
                    
                    Text(summary)
                        .font(.body)
                        .padding(12)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                }
            }
            
            // Sentiment Card
            if let sentiment = thought.sentiment {
                VStack(spacing: 8) {
                    HStack {
                        Text(sentimentEmoji)
                            .font(.largeTitle)
                        
                        VStack(alignment: .leading) {
                            Text("Sentiment")
                                .font(.caption)
                                .foregroundColor(.gray)
                            
                            Text(sentiment.capitalized)
                                .font(.headline)
                                .foregroundColor(sentimentColor)
                        }
                        
                        Spacer()
                        
                        if let confidence = thought.confidence {
                            VStack(alignment: .trailing) {
                                Text("Confidence")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                                
                                Text(String(format: "%.1f%%", confidence * 100))
                                    .font(.headline)
                            }
                        }
                    }
                    .padding()
                    .background(sentimentColor.opacity(0.1))
                    .cornerRadius(8)
                }
            }
            
            // Timestamp
            HStack {
                Image(systemName: "clock")
                Text(formatDate(thought.createdAt))
                    .font(.caption)
                    .foregroundColor(.gray)
                
                Spacer()
            }
            .padding(.top, 8)
            
            Spacer()
        }
        .padding()
        .navigationTitle("Summary")
        .navigationBarTitleDisplayMode(.inline)
    }
    
    private func formatDate(_ dateString: String) -> String {
        // Simple date formatting
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: dateString) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateStyle = .medium
            displayFormatter.timeStyle = .short
            return displayFormatter.string(from: date)
        }
        return dateString
    }
}

// MARK: - Entries View

struct EntriesView: View {
    @StateObject private var viewModel = EntriesViewModel()
    
    var body: some View {
        VStack {
            if viewModel.isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if viewModel.entries.isEmpty {
                VStack(spacing: 12) {
                    Image(systemName: "inbox.fill")
                        .font(.largeTitle)
                        .foregroundColor(.gray)
                    
                    Text("No Thoughts Yet")
                        .fontWeight(.semibold)
                    
                    Text("Start by analyzing your first thought")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                List {
                    ForEach(viewModel.entries) { entry in
                        NavigationLink(destination: SummaryView(thought: entry)) {
                            EntryRow(thought: entry)
                        }
                    }
                }
                .listStyle(.plain)
            }
        }
        .navigationTitle("Entries")
        .onAppear {
            Task {
                await viewModel.loadEntries()
            }
        }
    }
}

// MARK: - Entry Row

struct EntryRow: View {
    let thought: Thought
    
    var sentimentColor: Color {
        switch thought.sentiment?.lowercased() {
        case "positive":
            return .green
        case "negative":
            return .red
        default:
            return .gray
        }
    }
    
    var sentimentEmoji: String {
        switch thought.sentiment?.lowercased() {
        case "positive":
            return "😊"
        case "negative":
            return "😟"
        default:
            return "😐"
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(thought.rawText)
                        .font(.body)
                        .fontWeight(.semibold)
                        .lineLimit(2)
                    
                    if let summary = thought.summary {
                        Text(summary)
                            .font(.caption)
                            .foregroundColor(.gray)
                            .lineLimit(1)
                    }
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text(sentimentEmoji)
                        .font(.title3)
                    
                    if let sentiment = thought.sentiment {
                        Text(sentiment.prefix(3).uppercased())
                            .font(.caption2)
                            .fontWeight(.bold)
                            .foregroundColor(sentimentColor)
                    }
                }
            }
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Entries View Model

class EntriesViewModel: ObservableObject {
    @Published var entries: [Thought] = []
    @Published var isLoading = false
    
    private let apiService = APIService()
    
    func loadEntries() async {
        await MainActor.run {
            isLoading = true
        }
        
        do {
            let loaded = try await apiService.fetchEntries()
            await MainActor.run {
                entries = loaded
                isLoading = false
            }
        } catch {
            await MainActor.run {
                isLoading = false
            }
        }
    }
}

#Preview {
    NavigationStack {
        SummaryView(thought: Thought(
            id: 1,
            rawText: "Today was great",
            summary: "Had a positive day",
            sentiment: "positive",
            confidence: 0.85,
            createdAt: "2024-01-01T12:00:00Z"
        ))
    }
}
"""
