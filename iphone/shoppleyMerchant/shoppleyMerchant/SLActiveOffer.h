//
//  SLActiveOffer.h
//  shoppleyMerchant
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "SLOffer.h"

@interface SLActiveOffer : SLOffer {
    
}

@property (nonatomic, retain) NSNumber* redistributable;
@property (nonatomic, retain) NSNumber* redistributeProcessing;
@property (nonatomic, retain) NSNumber* isProcessing;

+ (NSArray*)offersArrayfromDictionary:(NSDictionary*)data;

- (void)populateFromDictionary:(NSDictionary*)data;

@end

@interface SLActiveOfferTableItem : TTTableLinkedItem {
    SLActiveOffer* _offer;
}

@property(nonatomic,retain) SLActiveOffer* offer;

+ (id)itemWithOffer:(SLActiveOffer*)offer URL:(NSString*)URL;

@end
