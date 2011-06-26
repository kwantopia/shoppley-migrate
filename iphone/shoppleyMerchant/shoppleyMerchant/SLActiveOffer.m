//
//  SLActiveOffer.m
//  shoppleyMerchant
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLActiveOffer.h"

@implementation SLActiveOffer
@synthesize redistributable, redistributeProcessing, isProcessing;

- (void)dealloc {
    TT_RELEASE_SAFELY(redistributable);
    TT_RELEASE_SAFELY(redistributeProcessing);
    TT_RELEASE_SAFELY(isProcessing);
    [super dealloc];
}

+ (NSArray*)offersArrayfromDictionary:(NSDictionary*)data {
    NSMutableArray* outputArray = [[[NSMutableArray alloc] init] autorelease];
    
    NSArray* offers = [data objectForKey:@"offers"];
    for (int i = 0; i < [offers count]; i++) {
        SLActiveOffer* offer = [[[SLActiveOffer alloc] init] autorelease];
        [offer populateFromDictionary:[offers objectAtIndex:i]];
        [outputArray addObject:offer];
    }
    
    return outputArray;
}

- (void)populateFromDictionary:(NSDictionary*)data {
    [super populateFromDictionary:data];
    self.redistributable = [data objectForKey:@"redistributable"];
    self.redistributeProcessing = [data objectForKey:@"redistributeProcessing"];
    self.isProcessing = [data objectForKey:@"isProcessing"];
}

#pragma mark -
#pragma mark NSCoding

- (id)initWithCoder:(NSCoder*)decoder {
    if ((self = [super initWithCoder:decoder])) {
        self.redistributable = [decoder decodeObjectForKey:@"redistributable"];
        self.redistributeProcessing = [decoder decodeObjectForKey:@"redistributeProcessing"];
        self.isProcessing = [decoder decodeObjectForKey:@"isProcessing"];
    }
    return self;
}

- (void)encodeWithCoder:(NSCoder*)encoder {
    [super encodeWithCoder:encoder];
    if (self.redistributable) {
        [encoder encodeObject:self.redistributable forKey:@"redistributable"];
    }
    if (self.redistributeProcessing) {
        [encoder encodeObject:self.redistributeProcessing forKey:@"redistributeProcessing"];
    }
    if (self.isProcessing) {
        [encoder encodeObject:self.isProcessing forKey:@"isProcessing"];
    }
}

@end

@implementation SLActiveOfferTableItem
@synthesize offer = _offer;

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    [super dealloc];
}

+ (id)itemWithOffer:(SLActiveOffer*)offer URL:(NSString *)URL {
    SLActiveOfferTableItem* item = [[[self alloc] init] autorelease];
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
