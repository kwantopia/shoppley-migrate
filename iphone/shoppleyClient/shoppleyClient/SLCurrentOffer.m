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

@end
