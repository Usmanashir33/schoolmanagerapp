// The exported code uses Tailwind CSS. Install Tailwind CSS in your dev environment to ensure all styles work.

import React, { useState, useEffect } from "react";
import { Link } from "react-router";

const Guides = () => {
  // Search and filter states
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [difficultyFilter, setDifficultyFilter] = useState("all");
  const [timeFilter, setTimeFilter] = useState("all");
  const [expandedCategories, setExpandedCategories] = useState([
    "getting-started",
    "advanced-features",
    "troubleshooting",
  ]);
  const [filteredGuides, setFilteredGuides] = useState([]);
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  // Guide data
  const guides = [
    {
      id: "g1",
      title: "Getting Started with the Platform",
      description:
        "Learn the basics of our platform and how to navigate the main features.",
      category: "getting-started",
      difficulty: "beginner",
      readTime: 10,
      lastUpdated: "2025-05-15",
      views: 1542,
      imageUrl:
        "https://readdy.ai/api/search-image?query=person%20using%20laptop%20with%20digital%20interface%2C%20modern%20workspace%2C%20clean%20desk%20setup%2C%20soft%20lighting%2C%20professional%20environment%2C%20high%20quality%20detailed%20image%20showing%20software%20onboarding%20process&width=300&height=200&seq=101&orientation=landscape",
    },
    {
      id: "g2",
      title: "Account Setup and Configuration",
      description:
        "Step-by-step guide to setting up your account and configuring your preferences.",
      category: "getting-started",
      difficulty: "beginner",
      readTime: 8,
      lastUpdated: "2025-05-20",
      views: 1289,
      imageUrl:
        "https://readdy.ai/api/search-image?query=person%20setting%20up%20digital%20account%20on%20computer%20screen%2C%20profile%20creation%20interface%2C%20modern%20office%20environment%2C%20soft%20lighting%2C%20professional%20workspace%2C%20high%20quality%20detailed%20image&width=300&height=200&seq=102&orientation=landscape",
    },
    {
      id: "g3",
      title: "Advanced Search Techniques",
      description:
        "Master the advanced search features to find exactly what you need quickly.",
      category: "advanced-features",
      difficulty: "intermediate",
      readTime: 15,
      lastUpdated: "2025-05-10",
      views: 876,
      imageUrl:
        "https://readdy.ai/api/search-image?query=person%20using%20advanced%20search%20interface%20on%20computer%2C%20data%20visualization%2C%20search%20filters%20displayed%2C%20modern%20office%20environment%2C%20professional%20workspace%2C%20high%20quality%20detailed%20image&width=300&height=200&seq=103&orientation=landscape",
    },
    {
      id: "g4",
      title: "Data Export and Reporting",
      description:
        "Learn how to export your data and create custom reports for analysis.",
      category: "advanced-features",
      difficulty: "advanced",
      readTime: 25,
      lastUpdated: "2025-05-05",
      views: 743,
      imageUrl:
        "https://readdy.ai/api/search-image?query=person%20analyzing%20data%20charts%20and%20graphs%20on%20computer%20screen%2C%20export%20interface%20visible%2C%20modern%20office%20environment%2C%20professional%20workspace%2C%20high%20quality%20detailed%20image%20showing%20data%20reporting&width=300&height=200&seq=104&orientation=landscape",
    },
    {
      id: "g5",
      title: "Troubleshooting Login Issues",
      description:
        "Common login problems and their solutions to get you back into your account.",
      category: "troubleshooting",
      difficulty: "beginner",
      readTime: 5,
      lastUpdated: "2025-05-25",
      views: 2341,
      imageUrl:
        "https://readdy.ai/api/search-image?query=person%20looking%20frustrated%20at%20login%20screen%20on%20computer%2C%20error%20message%20visible%2C%20modern%20office%20environment%2C%20professional%20workspace%2C%20high%20quality%20detailed%20image%20showing%20troubleshooting%20process&width=300&height=200&seq=105&orientation=landscape",
    },
    {
      id: "g6",
      title: "Resolving Data Sync Errors",
      description:
        "Diagnose and fix common data synchronization issues between devices.",
      category: "troubleshooting",
      difficulty: "intermediate",
      readTime: 18,
      lastUpdated: "2025-05-12",
      views: 967,
      imageUrl:
        "https://readdy.ai/api/search-image?query=person%20working%20with%20multiple%20devices%20showing%20sync%20error%20messages%2C%20troubleshooting%20interface%2C%20modern%20office%20environment%2C%20professional%20workspace%2C%20high%20quality%20detailed%20image&width=300&height=200&seq=106&orientation=landscape",
    },
    {
      id: "g7",
      title: "API Integration Guide",
      description:
        "Comprehensive guide to integrating our API with your existing systems.",
      category: "advanced-features",
      difficulty: "advanced",
      readTime: 35,
      lastUpdated: "2025-04-30",
      views: 658,
      imageUrl:
        "https://readdy.ai/api/search-image?query=person%20coding%20with%20API%20documentation%20open%2C%20code%20editor%20visible%2C%20integration%20diagram%2C%20modern%20office%20environment%2C%20professional%20workspace%2C%20high%20quality%20detailed%20image%20showing%20development%20process&width=300&height=200&seq=107&orientation=landscape",
    },
    {
      id: "g8",
      title: "Mobile App Features",
      description:
        "Explore all the features available in our mobile application.",
      category: "getting-started",
      difficulty: "beginner",
      readTime: 12,
      lastUpdated: "2025-05-18",
      views: 1876,
      imageUrl:
        "https://readdy.ai/api/search-image?query=person%20using%20smartphone%20with%20app%20interface%20visible%2C%20feature%20exploration%2C%20modern%20casual%20environment%2C%20soft%20lighting%2C%20high%20quality%20detailed%20image%20showing%20mobile%20application%20usage&width=300&height=200&seq=108&orientation=landscape",
    },
  ];

  // Categories data
  const categories = [
    {
      id: "getting-started",
      name: "Getting Started",
      count: guides.filter((g) => g.category === "getting-started").length,
    },
    {
      id: "advanced-features",
      name: "Advanced Features",
      count: guides.filter((g) => g.category === "advanced-features").length,
    },
    {
      id: "troubleshooting",
      name: "Troubleshooting",
      count: guides.filter((g) => g.category === "troubleshooting").length,
    },
  ];

  // Filter guides based on search and filter criteria
  useEffect(() => {
    let result = [...guides];

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (guide) =>
          guide.title.toLowerCase().includes(query) ||
          guide.description.toLowerCase().includes(query),
      );
    }

    // Apply category filter
    if (categoryFilter !== "all") {
      result = result.filter((guide) => guide.category === categoryFilter);
    }

    // Apply difficulty filter
    if (difficultyFilter !== "all") {
      result = result.filter((guide) => guide.difficulty === difficultyFilter);
    }

    // Apply time filter
    if (timeFilter !== "all") {
      switch (timeFilter) {
        case "short":
          result = result.filter((guide) => guide.readTime <= 15);
          break;
        case "medium":
          result = result.filter(
            (guide) => guide.readTime > 15 && guide.readTime <= 30,
          );
          break;
        case "long":
          result = result.filter((guide) => guide.readTime > 30);
          break;
      }
    }

    setFilteredGuides(result);
  }, [searchQuery, categoryFilter, difficultyFilter, timeFilter]);

  // Toggle category expansion
  const toggleCategory = (categoryId) => {
    setExpandedCategories((prev) =>
      prev.includes(categoryId)
        ? prev.filter((id) => id !== categoryId)
        : [...prev, categoryId],
    );
  };

  // Get difficulty badge color
  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case "beginner":
        return "bg-green-100 text-green-800";
      case "intermediate":
        return "bg-yellow-100 text-yellow-800";
      case "advanced":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  // Format read time
  const formatReadTime = (minutes) => {
    return `${minutes} min read`;
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb Navigation */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Link
                to={`/help-center`}
              className="hover:text-indigo-600 transition-colors duration-200 cursor-pointer"
            >
              <i className="fas fa-chevron-left mr-1"></i>
              Back to Support
            </Link>
            <span className="text-gray-400">/</span>
            <a
              href="#"
              className="hover:text-indigo-600 transition-colors duration-200 cursor-pointer"
            >
              Home
            </a>
            <span className="text-gray-400">/</span>
            <span className="font-medium text-indigo-600">Guides</span>
          </div>
        </div>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Guides & Instructions
          </h1>
          <p className="text-lg text-gray-600">
            Detailed instructions to help you make the most of our platform
          </p>
        </div>

        {/* Search and Filter Section */}
        <div className="mb-8 bg-white rounded-xl shadow-sm p-6">
          <div className="relative mb-6">
            <div
              className={`absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none transition-colors duration-200 ${isSearchFocused ? "text-indigo-600" : "text-gray-400"}`}
            >
              <i className="fas fa-search"></i>
            </div>
            <input
              type="text"
              placeholder="Search guides..."
              className="block w-full pl-10 pr-4 py-3 border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setIsSearchFocused(true)}
              onBlur={() => setIsSearchFocused(false)}
            />
          </div>

          <div className="grid grid-cols-4 md:grid-cols-3 gap-4">
            {/* Category Filter */}
            <div className="relative">
              <label
                htmlFor="category"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Category
              </label>
              <div className="relative">
                <select
                  id="category"
                  className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 rounded-md cursor-pointer"
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <option value="all">All Categories</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name} ({category.count})
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                  <i className="fas fa-chevron-down text-gray-400"></i>
                </div>
              </div>
            </div>

            {/* Difficulty Filter */}
            <div className="relative">
              <label
                htmlFor="difficulty"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Difficulty Level
              </label>
              <div className="relative">
                <select
                  id="difficulty"
                  className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 rounded-md cursor-pointer"
                  value={difficultyFilter}
                  onChange={(e) => setDifficultyFilter(e.target.value)}
                >
                  <option value="all">All Levels</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                  <i className="fas fa-chevron-down text-gray-400"></i>
                </div>
              </div>
            </div>

            {/* Time Filter */}
            <div className="relative">
              <label
                htmlFor="time"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Reading Time
              </label>
              <div className="relative">
                <select
                  id="time"
                  className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 rounded-md cursor-pointer"
                  value={timeFilter}
                  onChange={(e) => setTimeFilter(e.target.value)}
                >
                  <option value="all">Any Duration</option>
                  <option value="short">Short (5-15 mins)</option>
                  <option value="medium">Medium (15-30 mins)</option>
                  <option value="long">Long (30+ mins)</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                  <i className="fas fa-chevron-down text-gray-400"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Guides Content */}
        <div className="space-y-8">
          {/* Empty state */}
          {filteredGuides.length === 0 && (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <i className="fas fa-search text-3xl text-gray-400"></i>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No guides found
              </h3>
              <p className="text-gray-600 mb-6">
                Try adjusting your search or filter criteria
              </p>
              <button
                onClick={() => {
                  setSearchQuery("");
                  setCategoryFilter("all");
                  setDifficultyFilter("all");
                  setTimeFilter("all");
                }}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 !rounded-button whitespace-nowrap cursor-pointer"
              >
                Reset Filters
              </button>
            </div>
          )}

          {/* Guide Categories */}
          {filteredGuides.length > 0 &&
            categories.map((category) => {
              const categoryGuides = filteredGuides.filter(
                (guide) => guide.category === category.id,
              );

              if (categoryGuides.length === 0) return null;

              return (
                <div
                  key={category.id}
                  className="bg-white rounded-xl shadow-sm overflow-hidden"
                >
                  {/* Category Header */}
                  <div
                    className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex items-center justify-between cursor-pointer"
                    onClick={() => toggleCategory(category.id)}
                  >
                    <div className="flex items-center">
                      <h2 className="text-lg font-medium text-gray-900">
                        {category.name}
                      </h2>
                      <span className="ml-2 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {categoryGuides.length}{" "}
                        {categoryGuides.length === 1 ? "guide" : "guides"}
                      </span>
                    </div>
                    <button className="text-gray-400 hover:text-gray-600 focus:outline-none transition-colors duration-200 cursor-pointer">
                      <i
                        className={`fas fa-chevron-${expandedCategories.includes(category.id) ? "up" : "down"}`}
                      ></i>
                    </button>
                  </div>

                  {/* Category Guides */}
                  {expandedCategories.includes(category.id) && (
                    <div className="p-6 grid grid-cols-3 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {categoryGuides.map((guide) => (
                        <div
                          key={guide.id}
                          className="border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
                        >
                          <div className="h-40 overflow-hidden">
                            <img
                              src={guide.imageUrl}
                              alt={guide.title}
                              className="w-full h-full object-cover object-top transition-transform duration-500 hover:scale-105"
                            />
                          </div>
                          <div className="p-4">
                            <div className="flex items-center justify-between mb-2">
                              <span
                                className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(guide.difficulty)}`}
                              >
                                {guide.difficulty.charAt(0).toUpperCase() +
                                  guide.difficulty.slice(1)}
                              </span>
                              <span className="text-xs text-gray-500 flex items-center">
                                <i className="far fa-clock mr-1"></i>
                                {formatReadTime(guide.readTime)}
                              </span>
                            </div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2 line-clamp-2">
                              {guide.title}
                            </h3>
                            <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                              {guide.description}
                            </p>
                            <div className="flex items-center justify-between text-xs text-gray-500">
                              <span>
                                Updated{" "}
                                {new Date(guide.lastUpdated).toLocaleDateString(
                                  "en-US",
                                  {
                                    month: "short",
                                    day: "numeric",
                                    year: "numeric",
                                  },
                                )}
                              </span>
                              <span className="flex items-center">
                                <i className="far fa-eye mr-1"></i>
                                {guide.views.toLocaleString()}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
};

export default Guides;
