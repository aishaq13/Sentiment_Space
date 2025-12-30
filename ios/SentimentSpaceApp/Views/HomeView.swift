"""
Swift UI Views for Sentiment Space iOS app.
Exported as Swift code.
"""

swift_home_view = """
import SwiftUI

// MARK: - Home View

struct HomeView: View {
    @StateObject private var viewModel = HomeViewModel()
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                // Header
                VStack(alignment: .leading, spacing: 8) {
                    Text("Sentiment Space")
                        .font(.title)
                        .fontWeight(.bold)
                    
                    Text("Privacy-first thought analysis")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
                
                // Status
                if viewModel.backendStatus == "Connected" {
                    Label("Backend Connected", systemImage: "checkmark.circle.fill")
                        .foregroundColor(.green)
                        .padding(8)
                        .background(Color.green.opacity(0.1))
                        .cornerRadius(8)
                } else {
                    Label("Connecting...", systemImage: "circle.dotted")
                        .foregroundColor(.orange)
                        .padding(8)
                        .background(Color.orange.opacity(0.1))
                        .cornerRadius(8)
                }
                
                // Action Buttons
                VStack(spacing: 12) {
                    NavigationLink(destination: InputView()) {
                        HStack {
                            Image(systemName: "square.and.pencil")
                            Text("Analyze Thought")
                            Spacer()
                            Image(systemName: "chevron.right")
                        }
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                    }
                    
                    NavigationLink(destination: EntriesView()) {
                        HStack {
                            Image(systemName: "list.bullet")
                            Text("View Entries")
                            Spacer()
                            Text("\\(viewModel.thoughtCount)")
                                .fontWeight(.bold)
                        }
                        .padding()
                        .background(Color.purple)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                    }
                }
                .padding()
                
                // Privacy Notice
                VStack(alignment: .leading, spacing: 8) {
                    Label("Privacy First", systemImage: "lock.fill")
                        .fontWeight(.semibold)
                    
                    Text("All analysis runs locally on your device. No data leaves your device unless you explicitly export.")
                        .font(.caption)
                        .lineLimit(3)
                }
                .padding()
                .background(Color.green.opacity(0.1))
                .cornerRadius(8)
                
                Spacer()
            }
            .padding()
            .navigationTitle("Home")
        }
        .onAppear {
            viewModel.checkBackendStatus()
            viewModel.loadThoughtCount()
        }
    }
}

// MARK: - Home View Model

class HomeViewModel: ObservableObject {
    @Published var backendStatus = "Disconnected"
    @Published var thoughtCount = 0
    
    private let apiService = APIService()
    
    func checkBackendStatus() {
        Task {
            do {
                let isHealthy = try await apiService.healthCheck()
                await MainActor.run {
                    self.backendStatus = isHealthy ? "Connected" : "Disconnected"
                }
            } catch {
                await MainActor.run {
                    self.backendStatus = "Error"
                }
            }
        }
    }
    
    func loadThoughtCount() {
        Task {
            do {
                let entries = try await apiService.fetchEntries(limit: 1)
                await MainActor.run {
                    self.thoughtCount = entries.count
                }
            } catch {
                // Silently handle errors
            }
        }
    }
}

#Preview {
    HomeView()
}
"""
