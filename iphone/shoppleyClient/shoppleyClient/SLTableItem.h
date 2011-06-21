//
//  SLTableItem.h
//  shoppleyClient
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SLRightValueTableItem : TTTableCaptionItem {
    
}

+ (id)itemWithText:(NSString *)text value:(NSString *)value;

@end

@interface SLStarsTableItem : TTTableItem {
    NSNumber* _numberOfStars;
}

@property (nonatomic, copy) NSNumber* numberOfStars;

+ (id)itemWithNumberofStars:(NSNumber*)numberOfStars;

@end
