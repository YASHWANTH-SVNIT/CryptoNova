from django.shortcuts import render

ARTICLES = [
    {
        'title': 'What is Bitcoin?',
        'slug': 'what-is-bitcoin',
        'summary': 'Learn the basics of Bitcoin and how it works.',
        'content': '''Bitcoin is a decentralized digital currency, without a central bank or single administrator, that can be sent from user to user on the peer-to-peer Bitcoin network without the need for intermediaries. It was invented in 2008 by an unknown person or group of people using the name Satoshi Nakamoto.''',
        'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR5qyGGIfyRWJwICfWgmA1q8KWAH7gMe6GdMA&s',
    },
    {
        'title': 'How Blockchain Works',
        'slug': 'how-blockchain-works',
        'summary': 'Understand the revolutionary technology behind cryptocurrencies.',
        'content': '''Blockchain is a distributed database or ledger shared among a computer network's nodes. As a database, a blockchain stores information electronically in digital format. Blockchains are best known for their crucial role in cryptocurrency systems, such as Bitcoin, for maintaining a secure and decentralized record of transactions.''',
        'image': 'https://community.nasscom.in/sites/default/files/styles/960_x_600/public/media/images/loud%20%2811%29_0.png?itok=n_SwQmH7',
    },
    {
        'title': 'Ethereum and Smart Contracts',
        'slug': 'ethereum-and-smart-contracts',
        'summary': 'Dive into Ethereum and how smart contracts automate transactions.',
        'content': '''Ethereum is a decentralized blockchain platform that establishes a peer-to-peer network for securely executing and verifying application code, called smart contracts. Smart contracts allow participants to transact without a trusted central authority.''',
        'image': 'https://blockchain.oodles.io/wp-content/uploads/blockchain.oodles.io-5-1.jpg',
    },
    {
        'title': 'What are NFTs?',
        'slug': 'what-are-nfts',
        'summary': 'Explore the booming world of Non-Fungible Tokens (NFTs).',
        'content': '''NFTs, or Non-Fungible Tokens, are unique cryptographic tokens that exist on a blockchain and cannot be replicated. NFTs can represent digital ownership of artwork, music, videos, and even tweets.''',
        'image': '',
    },
    {
        'title': 'Introduction to DeFi',
        'slug': 'introduction-to-defi',
        'summary': 'Discover Decentralized Finance (DeFi) and its impact on banking.',
        'content': '''DeFi refers to a movement that uses decentralized networks and open-source software to create financial services and products. Anyone with an internet connection can access DeFi platforms without needing traditional banks.''',
        'image': '',
    },
    {
        'title': 'How to Store Crypto Safely',
        'slug': 'how-to-store-crypto-safely',
        'summary': 'Learn best practices for securing your digital assets.',
        'content': '''Cryptocurrency wallets can be hot (connected to the internet) or cold (offline storage). Keeping large amounts of crypto in a cold wallet, such as a hardware device, is generally considered safer.''',
        'image': '',
    },
]

def learn_home(request):
    return render(request, 'learn/learn_home.html', {'articles': ARTICLES})

def article_detail(request, slug):
    article = next((item for item in ARTICLES if item['slug'] == slug), None)
    return render(request, 'learn/article_detail.html', {'article': article})
