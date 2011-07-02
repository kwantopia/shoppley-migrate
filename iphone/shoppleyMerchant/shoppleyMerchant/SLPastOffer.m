//
//  SLPastOffer.m
//  shoppleyMerchant
//
//  Created by yod on 6/25/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLPastOffer.h"


@implementation SLPastOffer
@synthesize duration, amount, unit;

- (void)dealloc {
    TT_RELEASE_SAFELY(duration);
    TT_RELEASE_SAFELY(amount);
    TT_RELEASE_SAFELY(unit);
    [super dealloc];
}

+ (NSArray*)offersArrayfromDictionary:(NSDictionary*)data {
    NSMutableArray* outputArray = [[[NSMutableArray alloc] init] autorelease];
    
    NSArray* offers = [data objectForKey:@"offers"];
    for (int i = 0; i < [offers count]; i++) {
        SLPastOffer* offer = [[[SLPastOffer alloc] init] autorelease];
        [offer populateFromDictionary:[offers objectAtIndex:i]];
        [outputArray addObject:offer];
    }
    
    return outputArray;
}

- (void)populateFromDictionary:(NSDictionary*)data {
    [super populateFromDictionary:data];
    self.duration = [data objectForKey:@"duration"];
    self.amount = [data objectForKey:@"amount"];
    self.unit = [data objectForKey:@"unit"];
}

#pragma mark -
#pragma mark NSCoding

- (id)initWithCoder:(NSCoder*)decoder {
    if ((self = [super initWithCoder:decoder])) {
        self.duration = [decoder decodeObjectForKey:@"duration"];
        self.amount = [decoder decodeObjectForKey:@"amount"];
        self.unit = [decoder decodeObjectForKey:@"unit"];
    }
    return self;
}

- (void)encodeWithCoder:(NSCoder*)encoder {
    [super encodeWithCoder:encoder];
    if (self.duration) {
        [encoder encodeObject:self.duration forKey:@"duration"];
    }
    if (self.amount) {
        [encoder encodeObject:self.amount forKey:@"amount"];
    }
    if (self.unit) {
        [encoder encodeObject:self.unit forKey:@"unit"];
    }
}

@end

@implementation SLPastOfferTableItem
@synthesize offer = _offer;

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    [super dealloc];
}

+ (id)itemWithOffer:(SLPastOffer*)offer URL:(NSString *)URL {
    SLPastOfferTableItem* item = [[[self alloc] init] autorelease];
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
