"""
Swift model structures for Sentiment Space iOS app.
Exported as Swift code.
"""

swift_thought_model = """
import Foundation

// MARK: - Models

/// Represents a single thought analyzed by Sentiment Space
struct Thought: Identifiable, Codable {
    let id: Int
    let rawText: String
    let summary: String?
    let sentiment: String?
    let confidence: Double?
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case rawText = "raw_text"
        case summary
        case sentiment
        case confidence
        case createdAt = "created_at"
    }
}

/// Request model for analyzing new thought
struct AnalysisRequest: Codable {
    let rawText: String
    
    enum CodingKeys: String, CodingKey {
        case rawText = "raw_text"
    }
}

/// Response from analysis endpoint
struct AnalysisResponse: Codable {
    let id: Int
    let rawText: String
    let summary: String?
    let sentiment: String?
    let confidence: Double?
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case rawText = "raw_text"
        case summary
        case sentiment
        case confidence
        case createdAt = "created_at"
    }
    
    // Convert to Thought model
    func toThought() -> Thought {
        Thought(
            id: id,
            rawText: rawText,
            summary: summary,
            sentiment: sentiment,
            confidence: confidence,
            createdAt: createdAt
        )
    }
}

/// Response from entries endpoint
struct EntriesResponse: Codable {
    let total: Int
    let entries: [AnalysisResponse]
}

/// Sentiment classification
enum Sentiment: String, CaseIterable {
    case positive = "positive"
    case neutral = "neutral"
    case negative = "negative"
    
    var color: String {
        switch self {
        case .positive:
            return "green"
        case .neutral:
            return "gray"
        case .negative:
            return "red"
        }
    }
    
    var emoji: String {
        switch self {
        case .positive:
            return "😊"
        case .neutral:
            return "😐"
        case .negative:
            return "😟"
        }
    }
}
"""
