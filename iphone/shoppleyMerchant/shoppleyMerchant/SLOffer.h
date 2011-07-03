//
//  SLOffer.h
//  shoppleyMerchant
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SLOffer : NSObject <NSCoding> {

}

@property (nonatomic, retain) NSNumber* offerId;
@property (nonatomic, retain) NSString* name;
@property (nonatomic, retain) NSString* description;
@property (nonatomic, retain) NSString* img;
@property (nonatomic, retain) NSDate* expires;
@property (nonatomic, retain) NSNumber* redeemed;
@property (nonatomic, retain) NSNumber* received;

@property (readonly) NSNumber* redeemedPercentage;

- (void)populateFromDictionary:(NSDictionary*)data;

@end

@interface SLOfferTableItem : TTTableLinkedItem {
    
}

@end