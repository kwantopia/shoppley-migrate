//
//  SLNewOffer.h
//  shoppleyMerchant
//
//  Created by yod on 6/30/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SLNewOffer : NSObject {
    
}

@property (nonatomic, retain) NSString* name;
@property (nonatomic, retain) NSString* description;
@property (nonatomic, retain) NSDate* startTime;
@property (nonatomic, retain) NSNumber* duration;
@property (nonatomic, retain) NSNumber* amount;
@property (nonatomic, retain) NSNumber* unit;

@end
