//
//  SLOffer.m
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLOffer.h"


@implementation SLOffer
@synthesize offerId, name, merchantName, description, code, offerCodeId, img, phone, lat, lon;

- (void)dealloc {
    TT_RELEASE_SAFELY(offerId);
    TT_RELEASE_SAFELY(name);
    TT_RELEASE_SAFELY(merchantName);
    TT_RELEASE_SAFELY(description);
    TT_RELEASE_SAFELY(code);
    TT_RELEASE_SAFELY(offerCodeId);
    TT_RELEASE_SAFELY(img);
    TT_RELEASE_SAFELY(phone);
    TT_RELEASE_SAFELY(lat);
    TT_RELEASE_SAFELY(lon);
    [super dealloc];
}

- (void)populateFromDictionary:(NSDictionary*)data {
    self.offerId = [data objectForKey:@"offer_id"];
    self.name = [data objectForKey:@"name"];
    self.merchantName = [data objectForKey:@"merchant_name"];
    self.description = [data objectForKey:@"description"];
    self.code = [data objectForKey:@"code"];
    self.offerCodeId = [data objectForKey:@"offer_code_id"];
    self.img = [data objectForKey:@"img"];
    self.phone = [data objectForKey:@"phone"];
    self.lat = [data objectForKey:@"lat"];
    self.lon = [data objectForKey:@"lon"];
}

#pragma mark -
#pragma mark NSCoding

- (id)initWithCoder:(NSCoder*)decoder {
    if ((self = [self init])) {
        self.offerId = [decoder decodeObjectForKey:@"offerId"];
        self.name = [decoder decodeObjectForKey:@"name"];
        self.merchantName = [decoder decodeObjectForKey:@"merchantName"];
        self.description = [decoder decodeObjectForKey:@"description"];
        self.code = [decoder decodeObjectForKey:@"code"];
        self.offerCodeId = [decoder decodeObjectForKey:@"offerCodeId"];
        self.img = [decoder decodeObjectForKey:@"img"];
        self.phone = [decoder decodeObjectForKey:@"phone"];
        self.lat = [decoder decodeObjectForKey:@"lat"];
        self.lon = [decoder decodeObjectForKey:@"lon"];
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
    if (self.merchantName) {
        [encoder encodeObject:self.merchantName forKey:@"merchantName"];
    }
    if (self.description) {
        [encoder encodeObject:self.description forKey:@"description"];
    }
    if (self.code) {
        [encoder encodeObject:self.code forKey:@"code"];
    }
    if (self.offerCodeId) {
        [encoder encodeObject:self.offerCodeId forKey:@"offerCodeId"];
    }
    if (self.img) {
        [encoder encodeObject:self.img forKey:@"img"];
    }
    if (self.phone) {
        [encoder encodeObject:self.phone forKey:@"phone"];
    }
    if (self.lat) {
        [encoder encodeObject:self.lat forKey:@"lat"];
    }
    if (self.lon) {
        [encoder encodeObject:self.lon forKey:@"lon"];
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