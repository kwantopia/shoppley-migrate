//
//  SLCurrentOffer.m
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLCurrentOffer.h"

@implementation SLCurrentOffer
@synthesize expires;

+ (NSArray*)offersArrayfromDictionary:(NSDictionary*)data {
    NSMutableArray* outputArray = [[[NSMutableArray alloc] init] autorelease];
    
    NSArray* offers = [data objectForKey:@"offers"];
    for (int i = 0; i < [offers count]; i++) {
        SLCurrentOffer* offer = [[[SLCurrentOffer alloc] init] autorelease];
        [offer populateFromDictionary:[offers objectAtIndex:i]];
        [outputArray addObject:offer];
    }
    
    return outputArray;
}

- (void)populateFromDictionary:(NSDictionary*)data {
    [super populateFromDictionary:data];
    self.expires = [data objectForKey:@"expires"];
}

#pragma mark -
#pragma mark NSCoding

- (id)initWithCoder:(NSCoder*)decoder {
    if ((self = [super initWithCoder:decoder])) {
        self.expires = [decoder decodeObjectForKey:@"expires"];
    }
    return self;
}

- (void)encodeWithCoder:(NSCoder*)encoder {
    [super encodeWithCoder:encoder];
    if (self.expires) {
        [encoder encodeObject:self.expires forKey:@"expires"];
    }
}

@end

@implementation SLCurrentOfferTableItem
@synthesize offer = _offer;

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    [super dealloc];
}

+ (id)itemWithOffer:(SLCurrentOffer*)offer URL:(NSString *)URL {
    SLCurrentOfferTableItem* item = [[[self alloc] init] autorelease];
    item.URL = URL;
    item.offer = [offer retain];
    return item;
}

#pragma mark -
#pragma mark NSCoding

- (id)initWithCoder:(NSCoder*)decoder {
    if ((self = [super initWithCoder:decoder])) {
        self.offer = [decoder decodeObjectForKey:@"offer"];
    }
    return self;
}

- (void)encodeWithCoder:(NSCoder*)encoder {
    [super encodeWithCoder:encoder];
    if (self.offer) {
        [encoder encodeObject:self.offer forKey:@"offer"];
    }
}

@end
