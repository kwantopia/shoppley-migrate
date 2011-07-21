//
//  SLOffer.h
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SLOffer : NSObject <NSCoding> {

}

@property (nonatomic, retain) NSNumber* offerId;
@property (nonatomic, retain) NSString* name;
@property (nonatomic, retain) NSString* merchantName;
@property (nonatomic, retain) NSString* description;
@property (nonatomic, retain) NSString* code;
@property (nonatomic, retain) NSNumber* offerCodeId;
@property (nonatomic, retain) NSString* img;
@property (nonatomic, retain) NSString* banner;
@property (nonatomic, retain) NSString* phone;
@property (nonatomic, retain) NSNumber* lat;
@property (nonatomic, retain) NSNumber* lon;

- (void)populateFromDictionary:(NSDictionary*)data;

@end

@interface SLOfferTableItem : TTTableLinkedItem {
    
}

@end