//
//  SLRedeemedOffer.m
//  shoppleyClient
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLRedeemedOffer.h"


@implementation SLRedeemedOffer
@synthesize redeemedOn, txnAmount;

- (void)dealloc {
    TT_RELEASE_SAFELY(redeemedOn);
    TT_RELEASE_SAFELY(txnAmount);
    [super dealloc];
}

+ (NSArray*)offersArrayfromDictionary:(NSDictionary*)data {
    NSMutableArray* outputArray = [[[NSMutableArray alloc] init] autorelease];
    
    NSArray* offers = [data objectForKey:@"offers"];
    for (int i = 0; i < [offers count]; i++) {
        SLRedeemedOffer* offer = [[[SLRedeemedOffer alloc] init] autorelease];
        [offer populateFromDictionary:[offers objectAtIndex:i]];
        [outputArray addObject:offer];
    }
    
    return outputArray;
}

- (void)populateFromDictionary:(NSDictionary*)data {
    [super populateFromDictionary:data];
    self.redeemedOn = [data objectForKey:@"redeemed"];
    self.txnAmount = [data objectForKey:@"txn_amount"];
}

#pragma mark -
#pragma mark NSCoding

- (id)initWithCoder:(NSCoder*)decoder {
    if ((self = [super initWithCoder:decoder])) {
        self.redeemedOn = [decoder decodeObjectForKey:@"redeemed"];
        self.txnAmount = [decoder decodeObjectForKey:@"txn_amount"];
    }
    return self;
}

- (void)encodeWithCoder:(NSCoder*)encoder {
    [super encodeWithCoder:encoder];
    if (self.redeemedOn) {
        [encoder encodeObject:self.redeemedOn forKey:@"redeemed"];
        [encoder encodeObject:self.txnAmount forKey:@"txn_amount"];
    }
}

@end

@implementation SLRedeemedOfferTableItem
@synthesize offer = _offer;

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    [super dealloc];
}

+ (id)itemWithOffer:(SLRedeemedOffer*)offer URL:(NSString *)URL {
    SLRedeemedOfferTableItem* item = [[[self alloc] init] autorelease];
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

