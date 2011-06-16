//
//  SLCurrentOffer.h
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "SLOffer.h"

@interface SLCurrentOffer : SLOffer {
    
}

@property (nonatomic, retain) NSString* expires;

+ (NSArray*)offersArrayfromDictionary:(NSDictionary*)data;

- (void)populateFromDictionary:(NSDictionary*)data;

@end
