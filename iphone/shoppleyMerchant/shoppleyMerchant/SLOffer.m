//
//  SLOffer.m
//  shoppleyMerchant
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLOffer.h"


@implementation SLOffer
@synthesize offerId, name, description, img, expires, redeemed, received;

- (void)dealloc {
    TT_RELEASE_SAFELY(offerId);
    TT_RELEASE_SAFELY(name);
    TT_RELEASE_SAFELY(description);
    TT_RELEASE_SAFELY(img);
    TT_RELEASE_SAFELY(expires);
    TT_RELEASE_SAFELY(redeemed);
    TT_RELEASE_SAFELY(received);
    [super dealloc];
}

- (void)populateFromDictionary:(NSDictionary*)data {
    self.offerId = [data objectForKey:@"offer_id"];
    self.name = [data objectForKey:@"title"];
    self.description = [data objectForKey:@"description"];
    self.img = [data objectForKey:@"img"];
    self.expires = [data objectForKey:@"expires"];
    self.redeemed = [data objectForKey:@"redeemed"];
    self.received = [data objectForKey:@"received"];
}

#pragma mark -
#pragma mark NSCoding

- (id)initWithCoder:(NSCoder*)decoder {
    if ((self = [self init])) {
        self.offerId = [decoder decodeObjectForKey:@"offerId"];
        self.name = [decoder decodeObjectForKey:@"name"];
        self.description = [decoder decodeObjectForKey:@"description"];
        self.img = [decoder decodeObjectForKey:@"img"];
        self.expires = [decoder decodeObjectForKey:@"expires"];
        self.redeemed = [decoder decodeObjectForKey:@"redeemed"];
        self.received = [decoder decodeObjectForKey:@"received"];
    }
    
    return self;
}

- (void)encodeWithCoder:(NSCoder*)encoder {
    if (self.offerId) {
        [encoder encodeObject:self.offerId forKey:@"offerId"];
    }
    if (self.name) {
        [encoder encodeObject:self.name forKey:@"name"];
    }
    if (self.description) {
        [encoder encodeObject:self.description forKey:@"description"];
    }
    if (self.img) {
        [encoder encodeObject:self.img forKey:@"img"];
    }
    if (self.expires) {
        [encoder encodeObject:self.expires forKey:@"expires"];
    }
    if (self.redeemed) {
        [encoder encodeObject:self.redeemed forKey:@"redeemed"];
    }
    if (self.received) {
        [encoder encodeObject:self.received forKey:@"received"];
    }
}

@end

@implementation SLOfferTableItem

#pragma mark -
#pragma mark NSCoding

- (id)initWithCoder:(NSCoder*)decoder {
    if ((self = [super initWithCoder:decoder])) {
        
    }
    return self;
}

- (void)encodeWithCoder:(NSCoder*)encoder {
    [super encodeWithCoder:encoder];
}

@end