"""
Swift UI Input View for Sentiment Space iOS app.
Exported as Swift code.
"""

swift_input_view = """
import SwiftUI

// MARK: - Input View

struct InputView: View {
    @StateObject private var viewModel = InputViewModel()
    @Environment(\\.dismiss) var dismiss
    
    var body: some View {
        VStack(spacing: 16) {
            VStack(alignment: .leading, spacing: 8) {
                Text("Share Your Thought")
                    .font(.headline)
                
                TextEditor(text: $viewModel.text)
                    .frame(height: 200)
                    .padding(8)
                    .border(Color.gray.opacity(0.3))
                    .cornerRadius(8)
                
                HStack {
                    Spacer()
                    Text("\\(viewModel.text.count) characters")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            }
            
            if let error = viewModel.error {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.red)
                    .padding(8)
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(4)
            }
            
            Button(action: { Task { await viewModel.analyze() } }) {
                if viewModel.isLoading {
                    ProgressView()
                        .progressViewStyle(.circular)
                } else {
                    Text("Analyze")
                }
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(viewModel.text.isEmpty ? Color.gray : Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
            .disabled(viewModel.text.isEmpty || viewModel.isLoading)
            
            Spacer()
        }
        .padding()
        .navigationTitle("Analyze Thought")
        .navigationBarTitleDisplayMode(.inline)
        .onChange(of: viewModel.analysisComplete) { oldValue, newValue in
            if newValue {
                dismiss()
            }
        }
    }
}

// MARK: - Input View Model

class InputViewModel: ObservableObject {
    @Published var text = ""
    @Published var isLoading = false
    @Published var error: String?
    @Published var analysisComplete = false
    
    private let apiService = APIService()
    
    func analyze() async {
        guard !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            error = "Please enter some text"
            return
        }
        
        await MainActor.run {
            isLoading = true
            error = nil
        }
        
        do {
            let _ = try await apiService.analyzethought(text)
            await MainActor.run {
                isLoading = false
                analysisComplete = true
            }
        } catch let error as APIError {
            await MainActor.run {
                self.isLoading = false
                self.error = error.localizedDescription
            }
        } catch {
            await MainActor.run {
                isLoading = false
                self.error = "Unknown error occurred"
            }
        }
    }
}

#Preview {
    InputView()
}
"""
