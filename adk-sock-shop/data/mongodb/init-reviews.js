// Connection to the sockstore database
db = db.getSiblingDB('sockstore');

// Create the reviews collection
db.createCollection('reviews');

// Insert review data
db.reviews.insertMany([
  // Positive reviews for merino wool socks
  {
    _id: ObjectId(),
    productId: "sock-001",
    productName: "Classic Merino Wool Socks",
    customerId: "cust-101",
    customerName: "Alice Johnson",
    rating: 5,
    reviewText: "These merino wool socks are amazing! So soft and warm. I wish SockStore had more varieties of merino wool products.",
    keywords: ["merino", "wool", "warm", "soft", "comfortable"],
    date: new Date("2024-12-15"),
    verified: true
  },
  {
    _id: ObjectId(),
    productId: "sock-001",
    productName: "Classic Merino Wool Socks",
    customerId: "cust-102",
    customerName: "Bob Smith",
    rating: 5,
    reviewText: "Best wool socks I've ever owned. Please stock more merino wool options with different thickness levels!",
    keywords: ["merino", "wool", "quality", "durable"],
    date: new Date("2024-12-20"),
    verified: true
  },
  
  // Reviews for compression socks
  {
    _id: ObjectId(),
    productId: "sock-002",
    productName: "Athletic Compression Socks",
    customerId: "cust-103",
    customerName: "Carol Davis",
    rating: 4,
    reviewText: "Good compression socks for running. Would love to see medical-grade compression options.",
    keywords: ["compression", "athletic", "running", "sports"],
    date: new Date("2024-11-10"),
    verified: true
  },
  {
    _id: ObjectId(),
    productId: "sock-002",
    productName: "Athletic Compression Socks",
    customerId: "cust-104",
    customerName: "David Wilson",
    rating: 3,
    reviewText: "Compression is okay but not strong enough for my needs. Need higher compression levels.",
    keywords: ["compression", "athletic", "moderate"],
    date: new Date("2024-11-25"),
    verified: false
  },
  
  // Negative reviews for bamboo socks
  {
    _id: ObjectId(),
    productId: "sock-003",
    productName: "Eco Bamboo Socks",
    customerId: "cust-105",
    customerName: "Eve Martinez",
    rating: 2,
    reviewText: "Bamboo socks wore out quickly. Not impressed with the quality.",
    keywords: ["bamboo", "eco", "sustainable"],
    date: new Date("2024-10-05"),
    verified: true
  },
  {
    _id: ObjectId(),
    productId: "sock-003",
    productName: "Eco Bamboo Socks",
    customerId: "cust-106",
    customerName: "Frank Brown",
    rating: 2,
    reviewText: "Expected better from bamboo material. Prefer cotton or wool.",
    keywords: ["bamboo", "eco", "disappointing"],
    date: new Date("2024-10-20"),
    verified: true
  },
  
  // Mixed reviews for waterproof socks
  {
    _id: ObjectId(),
    productId: "sock-004",
    productName: "Waterproof Hiking Socks",
    customerId: "cust-107",
    customerName: "Grace Lee",
    rating: 4,
    reviewText: "Great waterproof socks! Would love more waterproof options for different activities.",
    keywords: ["waterproof", "hiking", "outdoor", "moisture"],
    date: new Date("2024-09-15"),
    verified: true
  },
  {
    _id: ObjectId(),
    productId: "sock-004",
    productName: "Waterproof Hiking Socks",
    customerId: "cust-108",
    customerName: "Henry Taylor",
    rating: 3,
    reviewText: "Waterproof feature works but they're too bulky for everyday wear.",
    keywords: ["waterproof", "bulky", "hiking"],
    date: new Date("2024-09-30"),
    verified: false
  },
  
  // Reviews for thermal socks
  {
    _id: ObjectId(),
    productId: "sock-005",
    productName: "Thermal Winter Socks",
    customerId: "cust-109",
    customerName: "Iris White",
    rating: 5,
    reviewText: "Perfect for winter! Please add more thermal options with different materials.",
    keywords: ["thermal", "winter", "warm", "insulated"],
    date: new Date("2024-08-01"),
    verified: true
  },
  {
    _id: ObjectId(),
    productId: "sock-005",
    productName: "Thermal Winter Socks",
    customerId: "cust-110",
    customerName: "Jack Anderson",
    rating: 4,
    reviewText: "Very warm but wish they had thermal socks with moisture-wicking properties.",
    keywords: ["thermal", "warm", "winter", "moisture-wicking"],
    date: new Date("2024-08-15"),
    verified: true
  },
  
  // Reviews for antibacterial socks
  {
    _id: ObjectId(),
    productId: "sock-006",
    productName: "Silver-Infused Antibacterial Socks",
    customerId: "cust-111",
    customerName: "Karen Miller",
    rating: 5,
    reviewText: "Love the antibacterial feature! No more odor. Want more antibacterial options!",
    keywords: ["antibacterial", "silver", "odor-control", "hygienic"],
    date: new Date("2024-07-10"),
    verified: true
  },
  {
    _id: ObjectId(),
    productId: "sock-006",
    productName: "Silver-Infused Antibacterial Socks",
    customerId: "cust-112",
    customerName: "Leo Garcia",
    rating: 4,
    reviewText: "Great for gym use. Would buy more antibacterial socks if available.",
    keywords: ["antibacterial", "gym", "sports", "odor-free"],
    date: new Date("2024-07-25"),
    verified: true
  }
]);

// Create indexes to improve search performance
db.reviews.createIndex({ keywords: 1 });
db.reviews.createIndex({ rating: -1 });
db.reviews.createIndex({ date: -1 });
db.reviews.createIndex({ "$**": "text" }); // Full-text search index

print("Database initialized with sample reviews!");