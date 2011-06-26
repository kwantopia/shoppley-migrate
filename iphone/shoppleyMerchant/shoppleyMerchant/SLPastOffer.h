//
//  SLPastOffer.h
//  shoppleyMerchant
//
//  Created by yod on 6/25/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "SLOffer.h"

@interface SLPastOffer : SLOffer {
    
}

+ (NSArray*)offersArrayfromDictionary:(NSDictionary*)data;

- (void)populateFromDictionary:(NSDictionary*)data;

@end

@interface SLPastOfferTableItem : TTTableLinkedItem {
    SLPastOffer* _offer;
}

@property(nonatomic,retain) SLPastOffer* offer;

+ (id)itemWithOffer:(SLPastOffer*)offer URL:(NSString*)URL;

@end
