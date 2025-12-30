"""
Swift API service for communicating with backend.
Exported as Swift code.
"""

swift_api_service = """
import Foundation

// MARK: - API Service

class APIService: NSObject, ObservableObject {
    @Published var isLoading = false
    @Published var error: String?
    
    private let backendURL: URL
    
    init(backendURL: String = "http://localhost:8000") {
        guard let url = URL(string: backendURL) else {
            fatalError("Invalid backend URL")
        }
        self.backendURL = url
    }
    
    // MARK: - Public Methods
    
    /// Analyze a thought using the backend
    func analyzethought(_ text: String) async throws -> Thought {
        let endpoint = backendURL.appendingPathComponent("analyze")
        
        let request = AnalysisRequest(rawText: text)
        var urlRequest = URLRequest(url: endpoint)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            throw APIError.encodingError
        }
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard httpResponse.statusCode == 200 else {
            throw APIError.httpError(httpResponse.statusCode)
        }
        
        do {
            let analysisResponse = try JSONDecoder().decode(
                AnalysisResponse.self,
                from: data
            )
            return analysisResponse.toThought()
        } catch {
            throw APIError.decodingError
        }
    }
    
    /// Fetch all stored thoughts
    func fetchEntries(limit: Int = 100, offset: Int = 0) async throws -> [Thought] {
        var endpoint = backendURL.appendingPathComponent("entries")
        var components = URLComponents(url: endpoint, resolvingAgainstBaseURL: true)!
        components.queryItems = [
            URLQueryItem(name: "limit", value: String(limit)),
            URLQueryItem(name: "offset", value: String(offset))
        ]
        
        guard let url = components.url else {
            throw APIError.invalidURL
        }
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard httpResponse.statusCode == 200 else {
            throw APIError.httpError(httpResponse.statusCode)
        }
        
        do {
            let entriesResponse = try JSONDecoder().decode(
                EntriesResponse.self,
                from: data
            )
            return entriesResponse.entries.map { $0.toThought() }
        } catch {
            throw APIError.decodingError
        }
    }
    
    /// Health check to verify backend is running
    func healthCheck() async throws -> Bool {
        let endpoint = backendURL.appendingPathComponent("health")
        
        do {
            let (_, response) = try await URLSession.shared.data(from: endpoint)
            if let httpResponse = response as? HTTPURLResponse {
                return httpResponse.statusCode == 200
            }
            return false
        } catch {
            return false
        }
    }
}

// MARK: - Error Handling

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(Int)
    case encodingError
    case decodingError
    case networkError
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid backend URL"
        case .invalidResponse:
            return "Invalid response from server"
        case .httpError(let code):
            return "HTTP Error: \\(code)"
        case .encodingError:
            return "Failed to encode request"
        case .decodingError:
            return "Failed to decode response"
        case .networkError:
            return "Network error"
        }
    }
}
"""
